import sys

class TinyBASU_Simulator:
    def __init__(self, prediction_method):
        # ثبات‌ها (۸ تا، ۱۶ بیتی)
        self.regs = [0] * 8
        # حافظه (۵۱۲ خانه، ۱۶ بیتی)
        self.memory = [0] * 512
        # شمارنده برنامه
        self.pc = 0
        # آمار عملکرد
        self.num_cycles = 0
        self.num_instructions = 0
        self.num_stalls = 0
        self.num_branches = 0
        self.num_correct_predictions = 0
        self.num_taken_branches = 0
        
        # متد پیش‌بینی (مثلاً 'ST', 'SN', 'D1', 'D2', 'IQ')
        self.prediction_method = prediction_method
        # جدول پیش‌بینی پرش (BPT)
        self.BPT = {}
        # دیکشنری برای نگهداری لیبل‌های برنامه
        self.labels = {}

    # ---------- بخش اسمبلر (تبدیل کد اسمبلی به باینری) ----------
    def parse_register(self, token):
        """تبدیل 'rx6' به عدد ۶"""
        if token.startswith('rx'):
            return int(token[2:])
        return None

    def assemble_file(self, inst_file):
        """دو مرحله‌ای: لیبل‌ها رو پیدا کن، سپس دستورات رو اسمبل کن"""
        with open(inst_file, 'r') as f:
            lines = f.readlines()

        # ----- مرحله ۱: پیدا کردن لیبل‌ها -----
        address = 0
        for line in lines:
            clean = line.strip()
            if not clean or clean.startswith('#'):
                continue
            if ':' in clean:
                label = clean.split(':')[0].strip()
                self.labels[label] = address
                # بعد از لیبل، ممکنه دستور هم باشه (مثل 'loop: add ...')
                parts = clean.split(':', 1)
                if len(parts) > 1 and parts[1].strip():
                    address += 1
            else:
                address += 1

        # ----- مرحله ۲: اسمبل کردن دستورات و پر کردن حافظه -----
        address = 0
        for line in lines:
            clean = line.strip()
            if not clean or clean.startswith('#'):
                continue
            
            # حذف لیبل از ابتدای خط (اگه وجود داشته باشه)
            if ':' in clean:
                parts = clean.split(':', 1)
                clean = parts[1].strip()
                if not clean:
                    continue
            
            # تجزیه دستور
            # جایگزین کاما با فاصله برای راحت split کردن
            clean = clean.replace(',', ' ')
            tokens = clean.split()
            if not tokens:
                continue
            
            mnemonic = tokens[0]
            operands = tokens[1:]

            # مقداردهی اولیه برای فیلدهای دستور
            opcode = 0
            rd = 0
            rs = 0
            rt = 0
            imm = 0
            func = 0

            # ---- تشخیص نوع دستور و پر کردن فیلدها ----
            if mnemonic == 'add':
                opcode = 0
                func = 1
                rd = self.parse_register(operands[0])
                rs = self.parse_register(operands[1])
                rt = self.parse_register(operands[2])
            elif mnemonic == 'sub':
                opcode = 0
                func = 2
                rd = self.parse_register(operands[0])
                rs = self.parse_register(operands[1])
                rt = self.parse_register(operands[2])
            elif mnemonic == 'slt':
                opcode = 0
                func = 4
                rd = self.parse_register(operands[0])
                rs = self.parse_register(operands[1])
                rt = self.parse_register(operands[2])
            elif mnemonic == 'addi':
                opcode = 1
                rd = self.parse_register(operands[0])
                rs = self.parse_register(operands[1])
                imm = int(operands[2]) & 0x7  # 3 بیت
            elif mnemonic == 'li':
                opcode = 2
                rd = self.parse_register(operands[0])
                imm = int(operands[1]) & 0x7
            elif mnemonic == 'lui':
                opcode = 3
                rd = self.parse_register(operands[0])
                imm = int(operands[1]) & 0x7
            elif mnemonic == 'lw':
                opcode = 4
                rd = self.parse_register(operands[0])
                rs = self.parse_register(operands[1])
                imm = int(operands[2]) & 0x7
            elif mnemonic == 'sw':
                opcode = 5
                rd = self.parse_register(operands[0])
                rs = self.parse_register(operands[1])
                imm = int(operands[2]) & 0x7
            elif mnemonic == 'beq':
                opcode = 10
                rd = self.parse_register(operands[0])  # در واقع rt
                rs = self.parse_register(operands[1])
                label = operands[2]
                offset = self.labels[label] - address
                imm = offset & 0x7  # 3 بیت کم‌تر
            elif mnemonic == 'bne':
                opcode = 11
                rd = self.parse_register(operands[0])
                rs = self.parse_register(operands[1])
                label = operands[2]
                offset = self.labels[label] - address
                imm = offset & 0x7
            elif mnemonic == 'jmp':
                opcode = 14
                label = operands[0]
                offset = self.labels[label] - address
                # آفست ۱۲ بیتی رو به ۴ بخش ۳ بیتی تقسیم کن
                full_imm = offset & 0xFFF  # 12 بیت
                rd = (full_imm >> 9) & 0x7
                rs = (full_imm >> 6) & 0x7
                rt = (full_imm >> 3) & 0x7
                imm = full_imm & 0x7
            elif mnemonic == 'jal':
                opcode = 15
                label = operands[0]
                offset = self.labels[label] - address
                full_imm = offset & 0xFFF
                rd = (full_imm >> 9) & 0x7
                rs = (full_imm >> 6) & 0x7
                rt = (full_imm >> 3) & 0x7
                imm = full_imm & 0x7
            else:
                raise ValueError(f"دستور ناشناخته: {mnemonic}")

            # ساخت کد ماشین ۱۶ بیتی
            instr = (opcode << 12) | (rd << 9) | (rs << 6) | (rt << 3) | imm
            self.memory[address] = instr
            address += 1

            # اگه حافظه دستورات پر شد (۲۵۶ خانه)، متوقف کن
            if address >= 256:
                break

    # ---------- مقداردهی اولیه حافظه ----------
    def init_memory(self, inst_file, data_file):
        # اسمبل کردن فایل دستورات
        self.assemble_file(inst_file)
        
        # بارگذاری فایل داده (از آدرس ۲۵۶ به بعد)
        try:
            with open(data_file, 'r') as f:
                lines = f.readlines()
            for i, line in enumerate(lines):
                line = line.strip()
                if line:
                    val = int(line, 16)  # اعداد هگزادسیمال
                    self.memory[256 + i] = val
        except FileNotFoundError:
            pass  # اگه فایل داده وجود نداشت، نادیده بگیر

    # ---------- گرفتن دستور از حافظه ----------
    def fetch(self):
        if self.pc < 0 or self.pc >= 512:
            return None, None
        instr = self.memory[self.pc]
        addr = self.pc
        self.pc += 1
        return instr, addr

    # ---------- دیکد کردن دستور ----------
    def decode(self, instr):
        opcode = (instr >> 12) & 0xF
        rd = (instr >> 9) & 0x7
        rs = (instr >> 6) & 0x7
        rt = (instr >> 3) & 0x7
        imm = instr & 0x7
        return opcode, rd, rs, rt, imm

    # ---------- گسترش علامت برای اعداد منفی ----------
    def sign_extend(self, value, bits):
        if value & (1 << (bits - 1)):
            return value - (1 << bits)
        return value

    # ---------- اجرای دستور ----------
    def execute(self, opcode, rd, rs, rt, imm):
        if opcode == 0:  # R-type
            func = imm
            if func == 1:  # add
                self.regs[rd] = (self.regs[rs] + self.regs[rt]) & 0xFFFF
            elif func == 2:  # sub
                self.regs[rd] = (self.regs[rs] - self.regs[rt]) & 0xFFFF
            elif func == 4:  # slt
                self.regs[rd] = 1 if self.regs[rs] < self.regs[rt] else 0
        elif opcode == 1:  # addi
            imm_s = self.sign_extend(imm, 3)
            self.regs[rd] = (self.regs[rs] + imm_s) & 0xFFFF
        elif opcode == 2:  # li
            self.regs[rd] = self.sign_extend(imm, 3)
        elif opcode == 3:  # lui
            self.regs[rd] = (imm << 8) & 0xFFFF
        elif opcode == 4:  # lw
            imm_s = self.sign_extend(imm, 3)
            addr = (self.regs[rs] + imm_s) & 0xFFFF
            if 256 <= addr <= 511:
                self.regs[rd] = self.memory[addr]
        elif opcode == 5:  # sw
            imm_s = self.sign_extend(imm, 3)
            addr = (self.regs[rs] + imm_s) & 0xFFFF
            if 256 <= addr <= 511:
                self.memory[addr] = self.regs[rd]
        elif opcode == 10:  # beq
            return (self.regs[rs] == self.regs[rd])  # rt = rd
        elif opcode == 11:  # bne
            return (self.regs[rs] != self.regs[rd])
        elif opcode == 14:  # jmp
            return True  # همیشه پرش
        elif opcode == 15:  # jal
            self.regs[7] = self.pc  # آدرس برگشت (PC+1)
            return True

    # ---------- پیش‌بینی پرش ----------
    def branch_prediction(self, opcode, pc):
        if opcode != 10 and opcode != 11:
            return None
        if self.prediction_method == 'ST':
            return True
        elif self.prediction_method == 'SN':
            return False
        elif self.prediction_method == 'D1':
            if pc not in self.BPT:
                self.BPT[pc] = 0
            return self.BPT[pc] == 1
        elif self.prediction_method == 'D2':
            if pc not in self.BPT:
                self.BPT[pc] = 0  # Strong Not Taken
            return self.BPT[pc] >= 2
        elif self.prediction_method == 'IQ':
            if pc not in self.BPT:
                self.BPT[pc] = 0
            return self.BPT[pc] >= 4  # 3-bit saturating
        return False

    # ---------- به‌روزرسانی جدول پیش‌بینی ----------
    def update_bpt(self, opcode, pc, actual_taken):
        if opcode != 10 and opcode != 11:
            return
        if self.prediction_method == 'D1':
            self.BPT[pc] = 1 if actual_taken else 0
        elif self.prediction_method == 'D2':
            if pc not in self.BPT:
                self.BPT[pc] = 0
            if actual_taken:
                self.BPT[pc] = min(3, self.BPT[pc] + 1)
            else:
                self.BPT[pc] = max(0, self.BPT[pc] - 1)
        elif self.prediction_method == 'IQ':
            if pc not in self.BPT:
                self.BPT[pc] = 0
            if actual_taken:
                self.BPT[pc] = min(7, self.BPT[pc] + 1)
            else:
                self.BPT[pc] = max(0, self.BPT[pc] - 1)

    # ---------- حلقه اصلی شبیه‌سازی ----------
    def simulate(self, timeout):
        while True:
            if self.num_cycles > timeout:
                print(f"⏰ Timeout! سیکل‌ها از {timeout} گذشت.")
                break

            instr, addr = self.fetch()
            if instr is None:
                break
            if instr == 0:  # ممکنه دستور NOP یا ته حافظه باشه
                # اگه به حافظه داده رسیدیم، تمومش کن
                if addr >= 256:
                    break
                # در غیر این صورت یه دستور واقعیه که مقدارش ۰ هست
                # (که خیلی کم پیش میاد، ولی نادیده میگیریمش)
                continue

            opcode, rd, rs, rt, imm = self.decode(instr)
            pc_fetch = addr

            # ---- پیش‌بینی برای دستورات شرطی ----
            predicted_taken = self.branch_prediction(opcode, pc_fetch)
            
            # ---- آدرس هدف برای پرش‌ها ----
            target = None
            if opcode == 10 or opcode == 11:
                imm_s = self.sign_extend(imm, 3)
                target = pc_fetch + imm_s
            elif opcode == 14 or opcode == 15:
                # آفست ۱۲ بیتی
                full_imm = (rd << 9) | (rs << 6) | (rt << 3) | imm
                full_imm = self.sign_extend(full_imm, 12)
                target = pc_fetch + full_imm

            # ---- اعمال پیش‌بینی (تغییر PC به صورت حدسی) ----
            if opcode == 10 or opcode == 11:
                if predicted_taken:
                    self.pc = target
                # else: self.pc همون PC+1 هست (که در fetch تنظیم شده)
            elif opcode == 14 or opcode == 15:
                self.pc = target

            # ---- اجرای واقعی دستور ----
            actual_taken = None
            if opcode == 10 or opcode == 11:
                actual_taken = self.execute(opcode, rd, rs, rt, imm)
            elif opcode == 14:
                self.execute(opcode, rd, rs, rt, imm)
            elif opcode == 15:
                # قبل از تغییر PC، آدرس برگشت رو ذخیره کن (در execute انجام میشه)
                self.execute(opcode, rd, rs, rt, imm)
            else:
                self.execute(opcode, rd, rs, rt, imm)

            # ---- مدیریت جریمه پرش و پیش‌بینی نادرست ----
            if opcode == 10 or opcode == 11:
                self.num_branches += 1
                # جریمه ۳ سیکل برای پرش‌های انجام‌شده (صرف نظر از پیش‌بینی)
                if actual_taken:
                    self.num_stalls += 3
                    self.num_cycles += 3
                    self.num_taken_branches += 1
                
                # اصلاح PC در صورت پیش‌بینی نادرست
                if predicted_taken != actual_taken:
                    # ۳ سیکل جریمه اضافه (در صورت نادرست بودن)
                    # ولی اگه actual_taken=True بود، قبلاً ۳ تا اضافه کردیم.
                    # اگه actual_taken=False بود و predicted=True بود، باید ۳ تا اضافه کنیم.
                    if not actual_taken:
                        self.num_stalls += 3
                        self.num_cycles += 3
                    # تصحیح PC
                    if actual_taken:
                        imm_s = self.sign_extend(imm, 3)
                        self.pc = pc_fetch + imm_s
                    else:
                        self.pc = pc_fetch + 1
                else:
                    # پیش‌بینی درست
                    self.num_correct_predictions += 1
                
                # به‌روزرسانی جدول پیش‌بینی
                self.update_bpt(opcode, pc_fetch, actual_taken)

            elif opcode == 14 or opcode == 15:
                # پرش غیرشرطی همیشه انجام میشه
                self.num_branches += 1
                self.num_taken_branches += 1
                self.num_stalls += 3
                self.num_cycles += 3

            # ---- آمار نهایی ----
            self.num_cycles += 1
            self.num_instructions += 1

    # ---------- تولید گزارش ----------
    def report(self, report_file):
        ipc = self.num_instructions / self.num_cycles if self.num_cycles > 0 else 0
        accuracy = (self.num_correct_predictions / self.num_branches * 100) if self.num_branches > 0 else 0
        # شتاب نسبت به حالت بدون پیش‌بینی (همیشه پرش انجام نشده)
        baseline_cycles = self.num_instructions + (self.num_taken_branches * 3)
        speedup = baseline_cycles / self.num_cycles if self.num_cycles > 0 else 1

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("===== گزارش شبیه‌ساز TinyBASU =====\n")
            f.write(f"روش پیش‌بینی: {self.prediction_method}\n")
            f.write(f"تعداد سیکل‌ها: {self.num_cycles}\n")
            f.write(f"تعداد دستورات اجرا شده: {self.num_instructions}\n")
            f.write(f"IPC (دستور در هر سیکل): {ipc:.4f}\n")
            f.write(f"تعداد توقف‌ها (جریمه پرش): {self.num_stalls}\n")
            f.write(f"تعداد پرش‌ها: {self.num_branches}\n")
            f.write(f"دقت پیش‌بینی پرش: {accuracy:.2f}%\n")
            f.write(f"شتاب نسبت به حالت بدون پیش‌بینی: {speedup:.4f}x\n")
            f.write("\n--- ثبات‌های نهایی ---\n")
            for i in range(8):
                f.write(f"r{i}: {self.regs[i]:04X} ({self.regs[i]})\n")
            f.write(f"شمارنده برنامه (PC): {self.pc}\n")
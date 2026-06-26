import sys

class TinyBASU_Simulator:
    def __init__(self, prediction_method):
        # registers (8 to 16 bits)
        self.regs = [0] * 8
        # memory
        self.memory = [0] * 512
        # Program Counter
        self.pc = 0
        # Performance stats
        self.num_cycles = 0
        self.num_instructions = 0
        self.num_stalls = 0
        self.num_branches = 0
        self.num_correct_predictions = 0
        self.num_taken_branches = 0
        
        # Prediction methods
        self.prediction_method = prediction_method
        # BPT
        self.BPT = {}
        # Dictionary to save the program labels
        self.labels = {}

    # assembler
    def parse_register(self, token):
        """Turn rx6 to number 6"""
        if token.startswith('rx'):
            return int(token[2:])
        return None

    def assemble_file(self, inst_file):
        """First find labels and then assemble them"""
        with open(inst_file, 'r') as f:
            lines = f.readlines()

        # Finding the labels
        address = 0
        for line in lines:
            clean = line.strip()
            if not clean or clean.startswith('#'):
                continue
             # Remove inline comments
            if '#' in clean:
                clean = clean.split('#')[0].strip()
                if not clean:
                    continue
            if ':' in clean:
                label = clean.split(':')[0].strip()
                self.labels[label] = address
                parts = clean.split(':', 1)
                if len(parts) > 1 and parts[1].strip():
                    address += 1
            else:
                address += 1

        # assemble the syntax
        address = 0
        for line in lines:
            clean = line.strip()
            if not clean or clean.startswith('#'):
                continue
            # Remove inline comments
            if '#' in clean:
                clean = clean.split('#')[0].strip()
                if not clean:
                    continue
            # remove the label
            if ':' in clean:
                parts = clean.split(':', 1)
                clean = parts[1].strip()
                if not clean:
                    continue
            
            # Syntax analysis
            clean = clean.replace(',', ' ')
            tokens = clean.split()
            if not tokens:
                continue
            
            mnemonic = tokens[0]
            operands = tokens[1:]

            # initializaztion
            opcode = 0
            rd = 0
            rs = 0
            rt = 0
            imm = 0
            func = 0

            # check the orders ti find out what are they
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
                imm = int(operands[2]) & 0x3F  # six bits
            elif mnemonic == 'li':
                opcode = 2
                rd = self.parse_register(operands[0])
                imm = int(operands[1]) & 0x3F
            elif mnemonic == 'lui':
                opcode = 3
                rd = self.parse_register(operands[0])
                imm = int(operands[1]) & 0x3F
            elif mnemonic == 'lw':
                opcode = 4
                rd = self.parse_register(operands[0])
                rs = self.parse_register(operands[1])
                imm = int(operands[2]) & 0x3F
            elif mnemonic == 'sw':
                opcode = 5
                rd = self.parse_register(operands[0])
                rs = self.parse_register(operands[1])
                imm = int(operands[2]) & 0x3F
            elif mnemonic == 'beq':
                opcode = 10
                rd = self.parse_register(operands[0])  # rt
                rs = self.parse_register(operands[1])
                label = operands[2]
                offset = self.labels[label] - address
                imm = offset & 0x3F  # 6 bits
            elif mnemonic == 'bne':
                opcode = 11
                rd = self.parse_register(operands[0])
                rs = self.parse_register(operands[1])
                label = operands[2]
                offset = self.labels[label] - address
                imm = offset & 0x3F
            elif mnemonic == 'jmp':
                opcode = 14
                label = operands[0]
                offset = self.labels[label] - address
                # turn 12 bits offset to 3 , 4 bits
                full_imm = offset & 0xFFF  # 12 bits
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
                raise ValueError(f"Unknown Command: {mnemonic}")

            # make 16 bits machine code
            instr = (opcode << 12) | (rd << 9) | (rs << 6) | (rt << 3) | imm
            self.memory[address] = instr
            address += 1

            # stop the program when the memory is full
            if address >= 256:
                break

    # initializing the memory
    def init_memory(self, inst_file, data_file):
        # assemble the command file
        self.assemble_file(inst_file)
        
        # upload the data file
        try:
            with open(data_file, 'r') as f:
                lines = f.readlines()
            for i, line in enumerate(lines):
                line = line.strip()
                if line:
                    val = int(line, 16)  # hexadecimal numbers
                    self.memory[256 + i] = val
        except FileNotFoundError:
            pass  # ignore if the data file doesn't exist

    # read the commands
    def fetch(self):
        if self.pc < 0 or self.pc >= 512:
            return None, None
        instr = self.memory[self.pc]
        addr = self.pc
        self.pc += 1
        return instr, addr

    # decode the commands
    def decode(self, instr):
        opcode = (instr >> 12) & 0xF
        rd = (instr >> 9) & 0x7
        rs = (instr >> 6) & 0x7
        rt = (instr >> 3) & 0x7
        if opcode == 0 or opcode == 14 or opcode == 15:  # R-type and J-type
            imm = instr & 0x7
        else:  # I-type: 6-bit immediate
            imm = instr & 0x3F
        return opcode, rd, rs, rt, imm

    # expantion for the signed numbers
    def sign_extend(self, value, bits):
        if value & (1 << (bits - 1)):
            return value - (1 << bits)
        return value

    # execute the command
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
            imm_s = self.sign_extend(imm, 6)
            self.regs[rd] = (self.regs[rs] + imm_s) & 0xFFFF
        elif opcode == 2:  # li
            self.regs[rd] = self.sign_extend(imm, 6)
        elif opcode == 3:  # lui
            self.regs[rd] = (imm << 10) & 0xFFFF
        elif opcode == 4:  # lw
            imm_s = self.sign_extend(imm, 6)
            addr = (self.regs[rs] + imm_s) & 0xFFFF
            if 256 <= addr <= 511:
                self.regs[rd] = self.memory[addr]
        elif opcode == 5:  # sw
            imm_s = self.sign_extend(imm, 6)
            addr = (self.regs[rs] + imm_s) & 0xFFFF
            if 256 <= addr <= 511:
                self.memory[addr] = self.regs[rd]
        elif opcode == 10:  # beq
            return (self.regs[rs] == self.regs[rd])  # rt = rd
        elif opcode == 11:  # bne
            return (self.regs[rs] != self.regs[rd])
        elif opcode == 14:  # jmp
            return True  # always jump
        elif opcode == 15:  # jal
            self.regs[7] = self.pc  # pc+1
            return True

    # jump prediction part
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

    # update the prediction table
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

    # simulation main loop
    def simulate(self, timeout):
        while True:
            if self.num_cycles > timeout:
                print(f"Timeout! Cycles exceeded {timeout}.")
                break

            instr, addr = self.fetch()
            if instr is None:
                break
            if instr == 0:  # NOP command
                # if rech the memory data finish
                if addr >= 256:
                    break
                continue

            opcode, rd, rs, rt, imm = self.decode(instr)
            pc_fetch = addr

            # prediction for conditional commands
            predicted_taken = self.branch_prediction(opcode, pc_fetch)
            
            # target address for the jump
            target = None
            if opcode == 10 or opcode == 11:
                imm_s = self.sign_extend(imm, 6)
                target = pc_fetch + imm_s
            elif opcode == 14 or opcode == 15:
                # 12 bits offset
                full_imm = (rd << 9) | (rs << 6) | (rt << 3) | imm
                full_imm = self.sign_extend(full_imm, 12)
                target = pc_fetch + full_imm

            # add the prediction
            if opcode == 10 or opcode == 11:
                if predicted_taken:
                    self.pc = target
                # else: pc = pc + 1
            elif opcode == 14 or opcode == 15:
                self.pc = target

            # excute the real commands
            actual_taken = None
            if opcode == 10 or opcode == 11:
                actual_taken = self.execute(opcode, rd, rs, rt, imm)
            elif opcode == 14:
                self.execute(opcode, rd, rs, rt, imm)
            elif opcode == 15:
                # save the address before the excute
                self.execute(opcode, rd, rs, rt, imm)
            else:
                self.execute(opcode, rd, rs, rt, imm)

            # jump and wrong prediction managment
            if opcode == 10 or opcode == 11:
                self.num_branches += 1
                if actual_taken:
                    self.num_taken_branches += 1
                
                # PC Correction
                if predicted_taken != actual_taken:
                    self.num_stalls += 3
                    self.num_cycles += 3
                    # correct the pc
                    if actual_taken:
                        imm_s = self.sign_extend(imm, 6)
                        self.pc = pc_fetch + imm_s
                    else:
                        self.pc = pc_fetch + 1
                else:
                    # right prediction
                    self.num_correct_predictions += 1
                
                # update the prediction teable
                self.update_bpt(opcode, pc_fetch, actual_taken)

            elif opcode == 14 or opcode == 15:
                # always excute the unconditional jumps
                self.num_branches += 1
                self.num_taken_branches += 1
                self.num_stalls += 3
                self.num_cycles += 3

            # finall stats
            self.num_cycles += 1
            self.num_instructions += 1

    # make the reports
    def report(self, report_file):
        ipc = self.num_instructions / self.num_cycles if self.num_cycles > 0 else 0
        accuracy = (self.num_correct_predictions / self.num_branches * 100) if self.num_branches > 0 else 0
        # Accesleration compared to the stats without prediction
        baseline_cycles = self.num_instructions + (self.num_taken_branches * 3)
        speedup = baseline_cycles / self.num_cycles if self.num_cycles > 0 else 1

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("****************Simulation report of TinyBASU**************\n")
            f.write(f"Prediction Method: {self.prediction_method}\n")
            f.write(f"Number of Cycles {self.num_cycles}\n")
            f.write(f"Number of Executed commands: {self.num_instructions}\n")
            f.write(f"IPC: {ipc:.4f}\n")
            f.write(f"Number of Stops: {self.num_stalls}\n")
            f.write(f"Number of jumps: {self.num_branches}\n")
            f.write(f"Prediction precision: {accuracy:.2f}%\n")
            f.write(f"Acceleration: {speedup:.4f}x\n")
            f.write("\n**********************Finall Registers********************\n")
            for i in range(8):
                f.write(f"r{i}: {self.regs[i]:04X} ({self.regs[i]})\n")
            f.write(f"PC: {self.pc}\n")
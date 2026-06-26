li rx1, 50                    # rx1 = 50 (عدد اولیه برای فاکتوریل)
li rx2, 1                     # rx2 = 1 (حاصل‌ضرب)

factorial_loop:
    # rx2 = rx2 × rx1 رو با جمع‌های مکرر انجام بده
    li rx3, 0                 # rx3 = 0 (مقدار اولیه برای جمع)
    li rx4, 0                 # rx4 = 0 (شمارنده برای جمع)
    
multiply_loop:
    add rx3, rx3, rx2         # rx3 = rx3 + rx2
    addi rx4, rx4, 1          # rx4 = rx4 + 1
    bne rx4, rx1, multiply_loop  # اگه rx4 != rx1، برگرد به جمع
    
    addi rx2, rx3, 0          # rx2 = rx3 (نتیجه ضرب رو بذار توی rx2)
    addi rx1, rx1, -1         # rx1 = rx1 - 1
    bne rx1, rx0, factorial_loop  # اگه rx1 != 0، برگرد به اول حلقه

# بعد از اتمام حلقه، rx2 = 50! هست
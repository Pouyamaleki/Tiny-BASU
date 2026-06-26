li rx6, 1                       # rx6 = 1 (Fibonacci number F0)
li rx1, 1                       # rx1 = 1 (Fibonacci number F1) 
addi rx2, rx0, 30               # rx2 = 20 (number of iterations)
addi rx3, rx0, 2                # rx3 = 2 (counter)

loop:
    add rx4, rx6, rx1           # rx4 = rx0 + rx1
    addi rx6, rx1, 0            # rx6 = rx1
    addi rx1, rx4, 0            # rx1 = rx4
    addi rx3, rx3, 1            # Increment the counter
    beq rx3, rx2, end           # Branch to last instruction
    jmp loop                      # Branch to last instruction

end: 
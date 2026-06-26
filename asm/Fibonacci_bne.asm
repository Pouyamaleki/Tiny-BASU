li rx6, 1                     # rx6 = 1
li rx1, 1                     # rx1 = 1
lui rx0, 0                    # rx0 = 0
addi rx2, rx0, 20             # rx2 = 20
addi rx3, rx0, 2              # rx3 = 2

loop:                         # loop label
    add rx4, rx6, rx1         # rx4 = rx6 + rx1
    addi rx6, rx1, 0          # rx6 = rx1
    addi rx1, rx4, 0          # rx1 = rx4
    addi rx3, rx3, 1          # add 1 to the counter (Counter++)
    bne rx3, rx2, loop        # if Counter != 20 go to loop 

add rx4, rx0, rx1             # put the twentith Fibonacci numer in the rx4 register
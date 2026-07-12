li rx1, 25                           # rx1 = 25
add rx1, rx1, rx1                    # rx1 = 50 (25 + 25)
li rx2, 1                            # rx2 = 1

factorial_loop:                      # Factorial loop label
    li rx3, 0                        # rx3 = 0
    li rx4, 0                        # rx4 = 0
    
    multiply_loop:                   # multiply loop label
        add rx3, rx3, rx2            # rx3 = rx3 + rx2
        addi rx4, rx4, 1             # rx4 = rx4 + 1
        bne rx4, rx1, multiply_loop  # if rx4 != rx1 go back to the multiply loop
    
    addi rx2, rx3, 0                 # rx2 = rx3
    addi rx1, rx1, -1                # rx1 = rx1 - 1
    bne rx1, rx0, factorial_loop     # if rx1 != rx0 go back to the first loop

add rx4, rx0, rx2                    # Store factorial result in rx4
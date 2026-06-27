li rx1, 6                        # rx1 = 6
li rx2, 4                        # rx2 = 4

mul rx3, rx1, rx2                # rx3 = 6 * 4 = 24
div rx4, rx3, rx2                # rx4 = 24 / 4 = 6

sll rx5, rx1, rx2                # rx5 = 6 << 4 = 96
srl rx5, rx5, rx2                # rx5 = 96 >> 4 = 6

slli rx0, rx1, 2                 # rx0 = 6 << 2 = 24
srli rx0, rx0, 1                 # rx0 = 24 >> 1 = 12

andi rx0, rx3, 15                # rx0 = 24 & 15 = 8
ori rx0, rx0, rx1                # rx0 = 8 | 6 = 14

li rx7, 10                       # rx7 = 10 (loop counter)
li rx6, 0                        # rx6 = 0 (accumulator)

sum_loop:                        # loop label
    add rx6, rx6, rx7            # rx6 = rx6 + rx7 (sum 10 + 9 + ... + 1)
    addi rx7, rx7, -1            # rx7 = rx7 - 1
    bgtz rx7, sum_loop           # if rx7 > 0 go to sum_loop

check_neg:                       # check negative number label
    li rx1, 3                    # rx1 = 3
    addi rx1, rx1, -5            # rx1 = 3 - 5 = -2 (negative)
    bltz rx1, done               # if rx1 < 0 jump to done
    li rx6, 0                    # this should NOT execute (skipped by bltz)

done:                            # end label
    addi rx5, rx6, 0             # rx5 = rx6 = 55 (final result)

# when the program finishes:
# rx3 = 24 (mul result)
# rx4 = 6  (div result)
# rx5 = 55 (sum 1 to 10 via bgtz loop)
# rx6 = 55 (accumulated sum)
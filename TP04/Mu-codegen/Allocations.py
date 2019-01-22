from Operands import Temporary, A0, SP, R0, R1, Indirect, Register
from Instruction3A import (Instru3A)

"""
MIF08, CAP, 2018
Allocation "replace" functions for direct code generation.
Each function suppose that its corresponding alloc has been called before.
"""


def replace_reg(old_i):
    """Replace Temporary operands with
    the corresponding allocated register."""
    ins, old_args = old_i.unfold()
    args = []
    for arg in old_args:
        if isinstance(arg, Temporary):
            arg = arg.get_alloced_loc()
            print(arg)
        args.append(arg)
    return [Instru3A(ins, args=args)]


def replace_mem(old_i):
    """Replace Temporary operands with the corresponding allocated
    memory location. SP points to the stack"""
    before = []
    after = []
    ins, old_args = old_i.unfold()
    args = []
    #Number of temp that we need to read (ie index > 0)
    nbTempRead = 0
    for (index,arg) in enumerate(old_args):
        if isinstance(arg, Temporary):
            #arg is an object of type Offset
            arg = arg.get_alloced_loc()

            if index > 0 or "print" in ins:
                #We need to access to this arg
                #So we have to load it from memory
                #And if index is 0 (first arg) but with print,
                # then we also need to read this arg


                reg = Register(nbTempRead)
                nbTempRead = nbTempRead+1

                before.append(Instru3A('getctr', SP, Indirect(reg)))
                before.append(Instru3A('add', reg, reg, arg.get_offset() * 16))
                before.append(Instru3A('setctr', A0, Indirect(reg)))
                before.append(Instru3A('readse', A0, 16, reg))

                arg = reg
            elif index == 0:
                #We need to write in this arg
                after.append(Instru3A('getctr', SP, Indirect(R0)))
                after.append(Instru3A('add', R0, R0, arg.get_offset() * 16))
                after.append(Instru3A('setctr', A0, Indirect(R0)))
                after.append(Instru3A('write', A0, 16, R1))
                arg = R1
                
        args.append(arg)

    i = Instru3A(ins, args=args)
    return before + [i] + after


def replace_smart(old_i):
    """Replace Temporary operands with the corresponding allocated
    physical register OR memory location."""
    before = []
    after = []
    ins, old_args = old_i.unfold()
    args = []
    # TODO: compute before,after,args. This is a superset of what replace_mem does.
    # and now return the new list!
    i = Instru3A(ins, args=args)  # change argument list into args
    return before + [i] + after

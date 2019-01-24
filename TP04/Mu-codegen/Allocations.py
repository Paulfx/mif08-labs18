from Operands import Temporary, A0, SP, R0, R1, Indirect, Register, Offset
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
            offset = arg.get_alloced_loc()

            reg, bf, aft, readingTemp = getBeforeAfterMemory(ins, index, nbTempRead, offset)
            before += bf
            after += aft
            if readingTemp:
                nbTempRead += 1



            """
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
            """
        else:
            reg = arg

        args.append(reg)

    i = Instru3A(ins, args=args)
    return before + [i] + after

def getBeforeAfterMemory(ins, indexArg, numberRegister, offset):
    before = []
    after = []
    readingTemp = False
    if indexArg > 0 or "print" in ins:
        #We need to access to this arg
        #So we have to load it from memory
        #And if indexArg is 0 (first arg) but with print,
        # then we also need to read this arg
        reg = Register(numberRegister)
        readingTemp = True

        before.append(Instru3A('getctr', SP, Indirect(reg)))
        before.append(Instru3A('add', reg, reg, offset.get_offset() * 16))
        before.append(Instru3A('setctr', A0, Indirect(reg)))
        before.append(Instru3A('readse', A0, 16, reg))


    elif indexArg == 0:
        #We need to write in this arg
        after.append(Instru3A('getctr', SP, Indirect(R0)))
        after.append(Instru3A('add', R0, R0, offset.get_offset() * 16))
        after.append(Instru3A('setctr', A0, Indirect(R0)))
        after.append(Instru3A('write', A0, 16, R1))
        reg = R1
    
    return reg, before, after, readingTemp

def replace_smart(old_i):
    """Replace Temporary operands with the corresponding allocated
    physical register OR memory location."""
    before = []
    after = []
    ins, old_args = old_i.unfold()
    args = []


    nbTempRead = 0

    for (index, arg) in enumerate(old_args):
        if isinstance(arg, Temporary):

            #Register of offset
            regOrOffset = arg.get_alloced_loc()

            if isinstance(regOrOffset, Offset):
                # We store in the memory
                newArg, bf, aft, readingTemp = getBeforeAfterMemory(ins, index, nbTempRead, regOrOffset)
                if readingTemp:
                    nbTempRead += 1
                before += bf
                after += aft
                args.append(newArg)

            else:
                assert isinstance(regOrOffset, Register)
                newArg = regOrOffset
        else:
            newArg = arg

        args.append(newArg)

    # TODO: compute before,after,args. This is a superset of what replace_mem does.
    # and now return the new list!
    i = Instru3A(ins, args=args)  # change argument list into args
    return before + [i] + after

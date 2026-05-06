from dataclasses import dataclass
from enum import Enum
from typing import Callable

from state import MachineState

class AddressMode(Enum):
    ACCUMULATOR = "ACCUMULATOR"
    IMPLIED = "IMPLIED"
    IMMEDIATE = "IMMEDIATE"
    ABSOLUTE = "ABSOLUTE"
    ZERO_PAGE = "ZERO_PAGE"
    RELATIVE = "RELATIVE"

@dataclass
class Instruction:
    name: str
    mode: AddressMode
    execute: Callable
    cycles: int
    # pattern: str # For the string pattern which will be used for this instruction

def ins_adc(state: MachineState, address : int) -> MachineState:
    """
    ADC - Add Memory to Accumulator with Carry

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    value = proc.read_byte(mem, address)
    carry = int(proc.flag_c)

    result = proc.reg_a + value + carry

    proc.flag_c = result > 0xFF
    proc.flag_v = bool((proc.reg_a ^ result) & (value ^ result) & 0x80)

    proc.reg_a = result & 0xFF

    proc.flag_z = (proc.reg_a == 0)
    proc.flag_n = (proc.reg_a & 0x80) != 0

    return MachineState(proc, mem)

def ins_and(state: MachineState, address : int) -> MachineState:
    """
    AND - AND Memory to Accumulator

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    value = proc.read_byte(mem, address)
    carry = int(proc.flag_c)

    proc.reg_a &= value
    proc.flag_z = (proc.reg_a == 0)
    proc.flag_n = (proc.reg_a & 0x80) != 0

    return MachineState(proc, mem)

def ins_asl(state: MachineState, address : int) -> MachineState:
    """
    ASL - Shift left 1 bit (Mem or ACC)

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    if address == -1:
        value = proc.reg_a
    else:
        value = proc.read_byte(mem, address)

    proc.flag_c = (value & 0x80) != 0
    result = (value << 1) & 0xFF

    proc.flag_z = (result == 0)
    proc.flag_n = (result & 0x80) != 0

    if address == -1:
        proc.reg_a = result
    else:
        proc.write_byte(mem, address, result)

    return MachineState(proc, mem)

def ins_bcc(state: MachineState, address : int) -> MachineState:
    """
    BCC - Branch on Carry Clear (Carry flag = 0)

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    if not proc.flag_c:
        proc.program_counter = address

    return MachineState(proc, mem)

def ins_bcs(state: MachineState, address : int) -> MachineState:
    """
    BCC - Branch on Carry Set (Carry flag = 1)

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    if proc.flag_c:
        proc.program_counter = address

    return MachineState(proc, mem)

def ins_beq(state: MachineState, address : int) -> MachineState:
    """
    BEQ - Branch on Result Zero (Zero flag = 1)

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    if proc.flag_z:
        proc.program_counter = address

    return MachineState(proc, mem)

def ins_bit(state: MachineState, address : int) -> MachineState:
    """
    BIT - Tests Bits in Mem with ACC

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    value = proc.read_byte(mem, address)
    proc.flag_z = (proc.reg_a & value) == 0     # ANDing the referenced value, setting Zero flag if the result is 0
    proc.flag_n = (value & 0x80) != 0           # Bit 7 sets the Negative flag
    proc.flag_v = (value & 0x40) != 0           # Bit 6 sets the Overflow flag

    return MachineState(proc, mem)

def ins_bmi(state: MachineState, address : int) -> MachineState:
    """
    BMI - Branch on Result Minus (Negative flag = 1)

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    if proc.flag_n:
        proc.program_counter = address

    return MachineState(proc, mem)

def ins_bne(state: MachineState, address : int) -> MachineState:
    """
    BNE - Branch on Result not Zero (Zero flag = 0)

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    if not proc.flag_z:
        proc.program_counter = address

    return MachineState(proc, mem)

def ins_bpl(state: MachineState, address : int) -> MachineState:
    """
    BPL - Branch on Result Plus (Negative flag = 0)

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    if not proc.flag_n:
        proc.program_counter = address

    return MachineState(proc, mem)

def ins_brk(state: MachineState, address: int) -> MachineState:
    """
    BRK - Software Break (IMPLIED ONLY)

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """

    raise StopIteration("BRK instruction reached, halting execution...")

def ins_bvc(state: MachineState, address : int) -> MachineState:
    """
    BVC - Branch on Overflow Clear (Overflow flag = 0)

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    if not proc.flag_v:
        proc.program_counter = address

    return MachineState(proc, mem)

def ins_bvs(state: MachineState, address : int) -> MachineState:
    """
    BVS - Branch on Overflow Set (Overflow flag = 1)

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    if proc.flag_z:
        proc.program_counter = address

    return MachineState(proc, mem)

def ins_clc(state: MachineState, address : int) -> MachineState:
    """
    CLC - Clear Carry Flag.

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    proc.flag_c = False

    return MachineState(proc, mem)

def ins_cld(state: MachineState, address : int) -> MachineState:
    """
    CLD - Clear Decimal Flag.

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    proc.flag_d = False

    return MachineState(proc, mem)

def ins_cli(state: MachineState, address : int) -> MachineState:
    """
    CLI - Clear Interrupt Flag.

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    proc.flag_i = False

    return MachineState(proc, mem)

def ins_clv(state: MachineState, address : int) -> MachineState:
    """
    CLV - Clear Overflow Flag.

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    proc.flag_v = False

    return MachineState(proc, mem)

def ins_cmp(state: MachineState, address : int) -> MachineState:
    """
    CMP - Compare Memory with ACC

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    value = proc.read_byte(mem, address)
    result = proc.reg_a - value

    proc.flag_c = proc.reg_a >= value
    proc.flag_z = proc.reg_a == value
    proc.flag_n = ((result & 0xFF) & 0x80) != 0

    return MachineState(proc, mem)

def ins_cpx(state: MachineState, address : int) -> MachineState:
    """
    CPX - Compare Memory and Index X

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    value = proc.read_byte(mem, address)
    result = proc.reg_x - value

    proc.flag_c = proc.reg_x >= value
    proc.flag_z = proc.reg_x == value
    proc.flag_n = ((result & 0xFF) & 0x80) != 0

    return MachineState(proc, mem)

def ins_cpy(state: MachineState, address : int) -> MachineState:
    """
    CPY - Compare Memory and Index Y

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    value = proc.read_byte(mem, address)
    result = proc.reg_y - value

    proc.flag_c = proc.reg_y >= value
    proc.flag_z = proc.reg_y == value
    proc.flag_n = ((result & 0xFF) & 0x80) != 0

    return MachineState(proc, mem)

def ins_dec(state: MachineState, address : int) -> MachineState:
    """
    DEC - Decrement Mem by 1

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    value = proc.read_byte(mem, address)

    value = (value - 1) & 0xFF
    proc.flag_z = (value == 0)
    proc.flag_n = (value & 0x80) != 0

    proc.write_byte(mem, address, value)

    return MachineState(proc, mem)


def ins_dex(state: MachineState, address: int) -> MachineState:
    """
    DEX - Decrement X by 1

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    proc.reg_x = (proc.reg_x - 1) & 0xFF
    proc.flag_z = (proc.reg_x == 0)
    proc.flag_n = (proc.reg_x & 0x80) != 0

    return MachineState(proc, mem)

def ins_dey(state: MachineState, address: int) -> MachineState:
    """
    DEY - Decrement Y by 1

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    proc.reg_y = (proc.reg_y - 1) & 0xFF
    proc.flag_z = (proc.reg_y == 0)
    proc.flag_n = (proc.reg_y & 0x80) != 0

    return MachineState(proc, mem)

def ins_eor(state: MachineState, address : int) -> MachineState:
    """
    EOR - XOR Mem with ACC

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    value = proc.read_byte(mem, address)

    proc.reg_a ^= value
    proc.flag_z = (proc.reg_a == 0)
    proc.flag_n = (proc.reg_a & 0x80) != 0

    return MachineState(proc, mem)

def ins_inc(state: MachineState, address : int) -> MachineState:
    """
    INC - Increment Mem by 1

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    value = proc.read_byte(mem, address)

    value = (value + 1) & 0xFF
    proc.flag_z = (value == 0)
    proc.flag_n = (value & 0x80) != 0

    return MachineState(proc, mem)

def ins_inx(state: MachineState, address : int) -> MachineState:
    """
    INX - Increment X by 1

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    proc.reg_x = (proc.reg_x + 1) & 0xFF
    proc.flag_z = (proc.reg_x == 0)
    proc.flag_n = (proc.reg_x & 0x80) != 0

    return MachineState(proc, mem)

def ins_iny(state: MachineState, address : int) -> MachineState:
    """
    INY - Increment Y by 1

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    proc.reg_y = (proc.reg_y + 1) & 0xFF
    proc.flag_z = (proc.reg_y == 0)
    proc.flag_n = (proc.reg_y & 0x80) != 0

    return MachineState(proc, mem)

def ins_jmp(state: MachineState, address : int) -> MachineState:
    """
    JMP - Jump to new location (Unconditional Jump)

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    proc.program_counter = address

    return MachineState(proc, mem)

def ins_jsr(state: MachineState, address : int) -> MachineState:
    """
    JSR - Jump to new location, saving return address to stack

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    return_address = (proc.program_counter - 1) & 0xFFFF
    proc.push_word(mem, return_address)
    proc.program_counter = address

    return MachineState(proc, mem)

def ins_lda(state : MachineState, address : int) -> MachineState:
    """
    LDA - Load ACC from Mem

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    proc.reg_a = proc.read_byte(mem, address)
    proc.flag_z = (proc.reg_a == 0)
    proc.flag_n = (proc.reg_a & 0x80) != 0

    return MachineState(proc, mem)

def ins_ldx(state : MachineState, address : int) -> MachineState:
    """
    LDX - Load X from Mem

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    proc.reg_x = proc.read_byte(mem, address)
    proc.flag_z = (proc.reg_x == 0)
    proc.flag_n = (proc.reg_x & 0x80) != 0

    return MachineState(proc, mem)

def ins_ldy(state : MachineState, address : int) -> MachineState:
    """
    LDY - Load Y from Mem

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    proc.reg_y = proc.read_byte(mem, address)
    proc.flag_z = (proc.reg_y == 0)
    proc.flag_n = (proc.reg_y & 0x80) != 0

    return MachineState(proc, mem)

def ins_lsr(state: MachineState, address : int) -> MachineState:
    """
    LSR - Shift right 1 bit (Mem or ACC)

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    if address == -1:
        value = proc.reg_a
    else:
        value = proc.read_byte(mem, address)

    proc.flag_c = (value & 0x01) != 0
    result = (value >> 1) & 0xFF

    proc.flag_z = (result == 0)
    proc.flag_n = False

    if address == -1:
        proc.reg_a = result
    else:
        proc.write_byte(mem, address, result)

    return MachineState(proc, mem)

def ins_nop(state: MachineState, address : int) -> MachineState:
    """
    NOP - No Operation.

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """
    proc: "Processor" = state.cpu
    mem: "Memory" = state.memory

    return MachineState(proc, mem)

def ins_ora(state: MachineState, address : int) -> MachineState:
    """
    ORA - OR Memory with Accumulator

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    value = proc.read_byte(mem, address)
    carry = int(proc.flag_c)

    proc.reg_a |= value
    proc.flag_z = (proc.reg_a == 0)
    proc.flag_n = (proc.reg_a & 0x80) != 0

    return MachineState(proc, mem)

def ins_pha(state: MachineState, address : int) -> MachineState:
    """
    PHA - Push ACC onto Stack

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    proc.push_byte(mem, proc.reg_a)

    return MachineState(proc, mem)

def ins_php(state: MachineState, address : int) -> MachineState:
    """
    PHP - Push processor status onto Stack

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    # N V - B D I Z C
    # N V 1 1 D I Z C

    state_values = (proc.flag_n << 7) + (proc.flag_v << 6) + (1 << 5) + (1 << 4) + (proc.flag_d << 3) + (proc.flag_i << 2) + (proc.flag_z << 1) + proc.flag_c

    proc.push_byte(mem, state_values)

    return MachineState(proc, mem)

def ins_pla(state: MachineState, address : int) -> MachineState:
    """
    PLA - Pop ACC from Stack

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    proc.reg_a = proc.pop_byte(mem)

    return MachineState(proc, mem)

def ins_plp(state: MachineState, address : int) -> MachineState:
    """
    PLP - Pop processor status from Stack

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    # N V - B D I Z C
    # N V # # D I Z C

    state_values = proc.pop_byte(mem)

    proc.flag_n = (state_values >> 7) & 1
    proc.flag_v = (state_values >> 6) & 1
    proc.flag_d = (state_values >> 3) & 1
    proc.flag_i = (state_values >> 2) & 1
    proc.flag_z = (state_values >> 1) & 1
    proc.flag_c = state_values & 1

    return MachineState(proc, mem)

def ins_rol(state: MachineState, address : int) -> MachineState:
    """
    ROL - Rotate one bit left (Mem or ACC)

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    if address == -1:
        value = proc.reg_a
    else:
        value = proc.read_byte(mem, address)

    old_carry = int(proc.flag_c)
    proc.flag_c = (value & 0x80) != 0
    result = (value << 1) & 0xFF | old_carry

    proc.flag_z = (result == 0)
    proc.flag_n = (result & 0x80) != 0

    if address == -1:
        proc.reg_a = result
    else:
        proc.write_byte(mem, address, result)

    return MachineState(proc, mem)

def ins_ror(state: MachineState, address : int) -> MachineState:
    """
    ROR - Rotate one bit right (Mem or ACC)

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    if address == -1:
        value = proc.reg_a
    else:
        value = proc.read_byte(mem, address)

    old_carry = int(proc.flag_c)
    proc.flag_c = (value & 0x01) != 0
    result = (value >> 1) | (old_carry << 7)

    proc.flag_z = (result == 0)
    proc.flag_n = (result & 0x80) != 0

    if address == -1:
        proc.reg_a = result
    else:
        proc.write_byte(mem, address, result)

    return MachineState(proc, mem)

def ins_rti(state: MachineState, address : int) -> MachineState:
    """
    RTI - Return from interrupt (Pull Processor Status, Pull Program Counter)

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    # N V - B D I Z C
    # N V # # D I Z C

    state_values = proc.pop_byte(mem)

    proc.flag_n = (state_values >> 7) & 1
    proc.flag_v = (state_values >> 6) & 1
    proc.flag_d = (state_values >> 3) & 1
    proc.flag_i = (state_values >> 2) & 1
    proc.flag_z = (state_values >> 1) & 1
    proc.flag_c = state_values & 1

    proc.reg_a = proc.pop_byte(mem)

    return MachineState(proc, mem)

def ins_rts(state: MachineState, address : int) -> MachineState:
    """
    RTS - Return from subroutine (Pull Program Counter, add 1 and make new PC)

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    proc.reg_a = proc.pop_byte(mem) + 1

    return MachineState(proc, mem)

def ins_sbc(state: MachineState, address : int) -> MachineState:
    """
    SBC - Subtract Memory from Accumulator with Carry

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc : 'Processor' = state.cpu
    mem : 'Memory' = state.memory

    value = proc.read_byte(mem, address) ^ 0xFF
    carry = int(proc.flag_c)

    result = proc.reg_a + value + carry

    proc.flag_c = result > 0xFF
    proc.flag_v = bool(((proc.reg_a ^ result) & (value ^ result) & 0x80) != 0)

    proc.reg_a = result & 0xFF

    proc.flag_z = (proc.reg_a == 0)
    proc.flag_n = (proc.reg_a & 0x80) != 0

    return MachineState(proc, mem)

def ins_sec(state: MachineState, address : int) -> MachineState:
    """
    SEC - Set Carry Flag.

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """
    proc: "Processor" = state.cpu
    mem: "Memory" = state.memory

    proc.flag_c = True

    return MachineState(proc, mem)

def ins_sed(state: MachineState, address : int) -> MachineState:
    """
    SED - Set Decimal Flag.

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """
    proc: "Processor" = state.cpu
    mem: "Memory" = state.memory

    proc.flag_d = True

    return MachineState(proc, mem)

def ins_sei(state: MachineState, address : int) -> MachineState:
    """
    SEI - Set Interrupt Flag.

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """
    proc: "Processor" = state.cpu
    mem: "Memory" = state.memory

    proc.flag_i = True

    return MachineState(proc, mem)

def ins_sta(state: MachineState, address : int) -> MachineState:
    """
    STA - Store Accumulator

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc: "Processor" = state.cpu
    mem: "Memory" = state.memory

    proc.write_byte(mem, address, proc.reg_a)
    return MachineState(proc, mem)

def ins_stx(state: MachineState, address : int) -> MachineState:
    """
    STX - Store X in Memory

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc: "Processor" = state.cpu
    mem: "Memory" = state.memory

    proc.write_byte(mem, address, proc.reg_x)
    return MachineState(proc, mem)

def ins_sty(state: MachineState, address : int) -> MachineState:
    """
    STY - Store Y in Memory

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc: "Processor" = state.cpu
    mem: "Memory" = state.memory

    proc.write_byte(mem, address, proc.reg_y)
    return MachineState(proc, mem)

def ins_tax(state: MachineState, address : int) -> MachineState:
    """
    TAX - Transfer Accumulator to X.

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """
    proc: "Processor" = state.cpu
    mem: "Memory" = state.memory

    proc.reg_x = proc.reg_a
    proc.flag_z = (proc.reg_x == 0)
    proc.flag_n = (proc.reg_x & 0x80) != 0

    return MachineState(proc, mem)

def ins_tay(state: MachineState, address : int) -> MachineState:
    """
    TAY - Transfer Accumulator to Y.

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """
    proc: "Processor" = state.cpu
    mem: "Memory" = state.memory

    proc.reg_y = proc.reg_a
    proc.flag_z = (proc.reg_y == 0)
    proc.flag_n = (proc.reg_y & 0x80) != 0

    return MachineState(proc, mem)

def ins_tsx(state: MachineState, address : int) -> MachineState:
    """
    TSX - Transfer Stack Pointer to X.

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """
    proc: "Processor" = state.cpu
    mem: "Memory" = state.memory

    proc.reg_x = proc.stack_pointer
    proc.flag_z = (proc.reg_x == 0)
    proc.flag_n = (proc.reg_x & 0x80) != 0

    return MachineState(proc, mem)

def ins_txa(state: MachineState, address : int) -> MachineState:
    """
    TXA - Transfer X to Accumulator.

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """
    proc: "Processor" = state.cpu
    mem: "Memory" = state.memory

    proc.reg_a = proc.reg_x
    proc.flag_z = (proc.reg_a == 0)
    proc.flag_n = (proc.reg_a & 0x80) != 0

    return MachineState(proc, mem)

def ins_txs(state: MachineState, address : int) -> MachineState:
    """
    TXA - Transfer X to Stack Register.

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """
    proc: "Processor" = state.cpu
    mem: "Memory" = state.memory

    proc.stack_pointer = proc.reg_x

    return MachineState(proc, mem)

def ins_tya(state: MachineState, address : int) -> MachineState:
    """
    TYA - Transfer Y to Accumulator.

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """
    proc: "Processor" = state.cpu
    mem: "Memory" = state.memory

    proc.reg_a = proc.reg_y
    proc.flag_z = (proc.reg_a == 0)
    proc.flag_n = (proc.reg_a & 0x80) != 0

    return MachineState(proc, mem)

instruction_table = {
    # ADC
    0x69: Instruction("ADC", AddressMode.IMMEDIATE, ins_adc, 2),
    0x65: Instruction("ADC", AddressMode.ZERO_PAGE, ins_adc, 3),
    0x6D: Instruction("ADC", AddressMode.ABSOLUTE, ins_adc, 4),

    # AND
    0x29: Instruction("AND", AddressMode.IMMEDIATE, ins_and, 2),
    0x25: Instruction("AND", AddressMode.ZERO_PAGE, ins_and, 3),
    0x2D: Instruction("AND", AddressMode.ABSOLUTE, ins_and, 4),

    # ASL
    0x0A: Instruction("ASL", AddressMode.ACCUMULATOR, ins_asl, 2),
    0x06: Instruction("ASL", AddressMode.ZERO_PAGE, ins_asl, 5),
    0x0E: Instruction("ASL", AddressMode.ABSOLUTE, ins_asl, 6),

    # BCC
    0x90: Instruction("BCC", AddressMode.RELATIVE, ins_bcc, 2),

    # BCS
    0xB0: Instruction("BCS", AddressMode.RELATIVE, ins_bcs, 2),

    # BEQ
    0xF0: Instruction("BEQ", AddressMode.RELATIVE, ins_beq, 2),

    # BIT
    0x24: Instruction("BIT", AddressMode.ZERO_PAGE, ins_bit, 3),
    0x2C: Instruction("BIT", AddressMode.ABSOLUTE,  ins_bit, 4),

    # BMI
    0x30: Instruction("BMI", AddressMode.RELATIVE, ins_bmi, 2),

    # BNE
    0xD0: Instruction("BEQ", AddressMode.RELATIVE,ins_bne, 2),

    # BPL
    0x10: Instruction("BPL", AddressMode.RELATIVE,ins_bpl, 2),

    # BRK
    0x00: Instruction("BRK", AddressMode.IMPLIED, ins_brk, 7),

    # BVC
    0x50: Instruction("BVC", AddressMode.IMPLIED, ins_bvc, 2),

    # BVS
    0x70: Instruction("BVS", AddressMode.IMPLIED, ins_bvc, 2),

    # CLC
    0x18: Instruction("CLC", AddressMode.IMPLIED, ins_clc, 2),

    # CLD
    0xD8: Instruction("CLD", AddressMode.IMPLIED, ins_cld, 2),

    # CLI
    0x58: Instruction("CLD", AddressMode.IMPLIED, ins_cli, 2),

    # CLV
    0xB8: Instruction("CLV", AddressMode.IMPLIED, ins_clv, 2),

    # CMP
    0xC9: Instruction("CMP", AddressMode.IMMEDIATE, ins_cmp, 2),
    0xC5: Instruction("CMP", AddressMode.ZERO_PAGE, ins_cmp, 3),
    0xCD: Instruction("CMP", AddressMode.ABSOLUTE,  ins_cmp, 4),

    # CPX
    0xE0: Instruction("CPX", AddressMode.IMMEDIATE, ins_cpx, 2),
    0xE4: Instruction("CPX", AddressMode.ZERO_PAGE, ins_cpx, 3),
    0xEC: Instruction("CPX", AddressMode.ABSOLUTE, ins_cpx, 4),

    # CPY
    0xC0: Instruction("CPY", AddressMode.IMMEDIATE, ins_cpy, 2),
    0xC4: Instruction("CPY", AddressMode.ZERO_PAGE, ins_cpy, 3),
    0xCC: Instruction("CPY", AddressMode.ABSOLUTE, ins_cpy, 4),

    # DEC
    0xC6: Instruction("DEC", AddressMode.ZERO_PAGE, ins_dec, 5),
    0xCE: Instruction("DEC", AddressMode.ABSOLUTE, ins_dec, 6),

    # DEX
    0xCA: Instruction("DEX", AddressMode.IMPLIED, ins_dex, 2),

    # DEY
    0x88: Instruction("DEY", AddressMode.IMPLIED, ins_dey, 2),

    # EOR
    0x49: Instruction("EOR", AddressMode.IMMEDIATE, ins_eor, 2),
    0x45: Instruction("EOR", AddressMode.ZERO_PAGE, ins_eor, 3),
    0x4D: Instruction("EOR", AddressMode.ABSOLUTE, ins_eor, 4),

    # INC
    0xE6: Instruction("INC", AddressMode.ZERO_PAGE, ins_inc, 5),
    0xEE: Instruction("INC", AddressMode.ABSOLUTE, ins_inc, 6),

    # INX
    0xE8: Instruction("INX", AddressMode.IMPLIED, ins_inx, 2),

    # INY
    0xC8: Instruction("INY", AddressMode.IMPLIED, ins_iny, 2),

    # JMP
    0x4C: Instruction("JMP", AddressMode.ABSOLUTE, ins_jmp, 3),

    # JSR
    0x20: Instruction("JSR", AddressMode.ABSOLUTE, ins_jsr, 6),

    # LDA
    0xA9: Instruction("LDA", AddressMode.IMMEDIATE, ins_lda, 2),
    0xA5: Instruction("LDA", AddressMode.ZERO_PAGE, ins_lda, 3),
    0xAD: Instruction("LDA", AddressMode.ABSOLUTE, ins_lda, 4),

    # LDX
    0xA2: Instruction("LDX", AddressMode.IMMEDIATE, ins_ldx, 2),
    0xA6: Instruction("LDX", AddressMode.ZERO_PAGE, ins_ldx, 3),
    0xAE: Instruction("LDX", AddressMode.ABSOLUTE, ins_ldx, 4),

    # LDY
    0xA0: Instruction("LDY", AddressMode.IMMEDIATE, ins_ldy, 2),
    0xA4: Instruction("LDY", AddressMode.ZERO_PAGE, ins_ldy, 3),
    0xAC: Instruction("LDY", AddressMode.ABSOLUTE, ins_ldy, 4),

    # LSR
    0x4A: Instruction("LSR", AddressMode.ACCUMULATOR, ins_lsr, 2),
    0x46: Instruction("LSR", AddressMode.ZERO_PAGE, ins_lsr, 5),
    0x4E: Instruction("LSR", AddressMode.ABSOLUTE, ins_lsr, 6),

    # NOP
    0xEA: Instruction("NOP", AddressMode.IMPLIED, ins_nop, 2),

    # ORA
    0x09: Instruction("ORA", AddressMode.IMMEDIATE, ins_ora, 2),
    0x05: Instruction("ORA", AddressMode.ZERO_PAGE, ins_ora, 3),
    0x0D: Instruction("ORA", AddressMode.ABSOLUTE, ins_ora, 4),

    # PHA
    0x48: Instruction("PHA", AddressMode.IMPLIED, ins_pha, 3),

    # PHP
    0x08: Instruction("PHP", AddressMode.IMPLIED, ins_php, 3),

    # PLA
    0x68: Instruction("PLA", AddressMode.IMPLIED, ins_pla, 4),

    # PLP
    0x28: Instruction("PLP", AddressMode.IMPLIED, ins_pla, 4),

    # ROL
    0x2A: Instruction("ROL", AddressMode.ACCUMULATOR, ins_rol, 2),
    0x26: Instruction("ROL", AddressMode.ZERO_PAGE, ins_rol, 5),
    0x2E: Instruction("ROL", AddressMode.ABSOLUTE, ins_rol, 6),

    # ROR
    0x6A: Instruction("ROR", AddressMode.ACCUMULATOR, ins_ror, 2),
    0x66: Instruction("ROR", AddressMode.ZERO_PAGE, ins_ror, 5),
    0x6E: Instruction("ROR", AddressMode.ABSOLUTE, ins_ror, 6),

    # RTI
    0x40: Instruction("RTI", AddressMode.IMPLIED, ins_rti, 6),

    # RTS
    0x60: Instruction("RTS", AddressMode.IMPLIED, ins_rts, 6),

    # SBC
    0xE9: Instruction("SBC", AddressMode.IMMEDIATE, ins_sbc, 2),
    0xE5: Instruction("SBC", AddressMode.ZERO_PAGE, ins_sbc, 3),
    0xED: Instruction("SBC", AddressMode.ABSOLUTE, ins_sbc, 4),

    # SEC
    0x38: Instruction("SEC", AddressMode.IMPLIED, ins_sec, 2),

    # SED
    0xF8: Instruction("SED", AddressMode.IMPLIED, ins_sed, 2),

    # SEI
    0x78: Instruction("SEI", AddressMode.IMPLIED, ins_sei, 2),

    # STA
    0x85: Instruction("STA", AddressMode.ZERO_PAGE, ins_sta, 3),
    0x8D: Instruction("STA", AddressMode.ABSOLUTE, ins_sta, 4),

    # STX
    0x86: Instruction("STX", AddressMode.ZERO_PAGE, ins_stx, 3),
    0x8E: Instruction("STX", AddressMode.ABSOLUTE, ins_stx, 4),

    # STY
    0x84: Instruction("STY", AddressMode.ZERO_PAGE, ins_sty, 3),
    0x8C: Instruction("STY", AddressMode.ABSOLUTE, ins_sty, 4),

    # TAX
    0xAA: Instruction("TAX", AddressMode.IMPLIED, ins_tax, 2),

    # TAY
    0xA8: Instruction("TAY", AddressMode.IMPLIED, ins_tay, 2),

    # TSX
    0xBA: Instruction("TSX", AddressMode.IMPLIED, ins_tsx, 2),

    # TXA
    0x8A: Instruction("TXA", AddressMode.IMPLIED, ins_txa, 2),

    # TXS
    0x9A: Instruction("TXS", AddressMode.IMPLIED, ins_txs, 2),

    # TYA
    0x98: Instruction("TYA", AddressMode.IMPLIED, ins_tya, 2),
}
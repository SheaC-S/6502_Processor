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
    proc = state.cpu
    mem = state.memory

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
    proc = state.cpu
    mem = state.memory

    value = proc.read_byte(mem, address)
    carry = int(proc.flag_c)

    proc.reg_a &= value
    proc.flag_z = (proc.reg_a == 0)

    return MachineState(proc, mem)

def ins_asl(state: MachineState, address : int) -> MachineState:
    """
    ASL - Shift left 1 bit (Mem or ACC)

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc = state.cpu
    mem = state.memory

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
    proc = state.cpu
    mem = state.memory

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
    proc = state.cpu
    mem = state.memory

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
    proc = state.cpu
    mem = state.memory

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
    proc = state.cpu
    mem = state.memory

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
    proc = state.cpu
    mem = state.memory

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
    proc = state.cpu
    mem = state.memory

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
    proc = state.cpu
    mem = state.memory

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
    proc = state.cpu
    mem = state.memory

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
    proc = state.cpu
    mem = state.memory

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
    proc = state.cpu
    mem = state.memory

    proc.flag_c = False

    return MachineState(proc, mem)

def ins_cld(state: MachineState, address : int) -> MachineState:
    """
    CLD - Clear Decimal Flag.

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """
    proc = state.cpu
    mem = state.memory

    proc.flag_d = False

    return MachineState(proc, mem)

def ins_cli(state: MachineState, address : int) -> MachineState:
    """
    CLI - Clear Interrupt Flag.

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """
    proc = state.cpu
    mem = state.memory

    proc.flag_i = False

    return MachineState(proc, mem)

def ins_clv(state: MachineState, address : int) -> MachineState:
    """
    CLV - Clear Overflow Flag.

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """
    proc = state.cpu
    mem = state.memory

    proc.flag_v = False

    return MachineState(proc, mem)

def ins_cmp(state: MachineState, address : int) -> MachineState:
    """
    CMP - Compare Memory with ACC

    :param state: Current MachineState of the console
    :param address: The specific type of addressing mode used
    :return: Modified MachineState
    """
    proc = state.cpu
    mem = state.memory

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
    proc = state.cpu
    mem = state.memory

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
    proc = state.cpu
    mem = state.memory

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
    proc = state.cpu
    mem = state.memory

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
    proc = state.cpu
    mem = state.memory

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
    proc = state.cpu
    mem = state.memory

    proc.reg_y = (proc.reg_y - 1) & 0xFF
    proc.flag_z = (proc.reg_y == 0)
    proc.flag_n = (proc.reg_y & 0x80) != 0

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

def ins_inx(state: MachineState, address : int) -> MachineState:
    """
    INX - Increment X Register.

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """
    proc: "Processor" = state.cpu
    mem: "Memory" = state.memory

    proc.reg_x = (proc.reg_x + 1) & 0xFF
    proc.flag_z = (proc.reg_x == 0)
    proc.flag_n = (proc.reg_x & 0x80) != 0

    return MachineState(proc, mem)

def ins_lda(state : MachineState, address : int) -> MachineState:
    """
    LDA - Load to Accumulator

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """
    proc: "Processor" = state.cpu
    mem: "Memory" = state.memory

    proc.reg_a = proc.read_byte(mem, address)
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
    0xCA: Instruction("DEX", AddressMode.ZERO_PAGE, ins_dex, 2),

    # DEY
    0x88: Instruction("DEY", AddressMode.ZERO_PAGE, ins_dey, 2),

    # INX
    0xE8: Instruction("INX", AddressMode.IMPLIED, ins_inx, 1),

    # LDA
    0xA9: Instruction("LDA", AddressMode.IMMEDIATE, ins_lda, 0),
    0xA5: Instruction("LDA", AddressMode.ZERO_PAGE, ins_lda, 1),
    0xAD: Instruction("LDA", AddressMode.ABSOLUTE, ins_lda, 2),

    # NOP
    0xEA: Instruction("NOP", AddressMode.IMPLIED, ins_nop, 1),

    # SEC
    0x38: Instruction("SEC", AddressMode.IMPLIED, ins_sec, 1),

    # STA
    0x85: Instruction("STA", AddressMode.ZERO_PAGE, ins_sta, 3),
    0x8D: Instruction("STA", AddressMode.ABSOLUTE, ins_sta, 4),

    # TAX
    0xAA: Instruction("TAX", AddressMode.IMPLIED, ins_tax, 1),


}
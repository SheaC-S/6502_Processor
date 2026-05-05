from dataclasses import dataclass
from enum import Enum
from typing import Callable

from state import MachineState

class AddressMode(Enum):
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

    value = proc.fetch_byte(mem, address)
    carry = int(proc.flag_c)

    result = proc.reg_a + value + carry

    proc.flag_c = result > 0xFF
    proc.flag_v = bool((proc.reg_a ^ result) & (value ^ result) & 0x80)

    proc.reg_a = result & 0xFF

    proc.flag_z = (proc.reg_a == 0)
    proc.flag_n = (proc.reg_a & 0x80) != 0

    return MachineState(proc, mem)

def ins_brk(state: MachineState, address: int) -> MachineState:
    """
    BRK - Software Break (IMPLIED ONLY)

    :param state: Current MachineState of the console
    :param address: NOT USED
    :return: Modified MachineState
    """

    raise StopIteration("BRK instruction reached, halting execution...")

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

    # BRK
    0x00: Instruction("BRK", AddressMode.IMPLIED, ins_brk, 7),

    # CLC
    0x18: Instruction("CLC", AddressMode.IMPLIED, ins_clc, 1),

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
from dataclasses import dataclass
from typing import Callable

from state import MachineState

@dataclass
class Instruction:
    name: str
    execute: Callable
    cycles: int
    # pattern: str # For the string pattern which will be used for this instruction

def ins_clc_imp(state: MachineState) -> MachineState:
    """
    CLC - Clear Carry Flag.

    :return: None
    """
    proc: "Processor" = state.cpu
    mem: "Memory" = state.memory

    proc.flag_c = False

    return MachineState(proc, mem)

def ins_sec_imp(state: MachineState) -> MachineState:
    """
    SEC - Set Carry Flag.

    :return: None
    """
    proc: "Processor" = state.cpu
    mem: "Memory" = state.memory

    proc.flag_c = True

    return MachineState(proc, mem)

def ins_nop_imp(state: MachineState) -> MachineState:
    """
    NOP - No Operation.

    :return: None
    """
    proc: "Processor" = state.cpu
    mem: "Memory" = state.memory

    return MachineState(proc, mem)

def ins_tax_imp(state: MachineState) -> MachineState:
    """
    TAX - Transfer Accumulator to X.

    :return: None
    """
    proc: "Processor" = state.cpu
    mem: "Memory" = state.memory

    proc.reg_x = proc.reg_a
    proc.flag_z = (proc.reg_x == 0)
    proc.flag_n = (proc.reg_x & 0x80) != 0

    return MachineState(proc, mem)

def ins_inx_imp(state: MachineState) -> MachineState:
    """
    INX - Increment X Register.

    :return: None
    """
    proc: "Processor" = state.cpu
    mem: "Memory" = state.memory

    proc.reg_x = (proc.reg_x + 1) & 0xFF
    proc.flag_z = (proc.reg_x == 0)
    proc.flag_n = (proc.reg_x & 0x80) != 0

    return MachineState(proc, mem)

def ins_lda_imm(state: MachineState) -> MachineState:
    """
    LDA - Load to Accumulator.

    :return: None
    """
    proc: "Processor" = state.cpu
    mem: "Memory" = state.memory

    proc.reg_a = proc.fetch_byte()
    proc.flag_z = (proc.reg_a == 0)
    proc.flag_n = (proc.reg_a & 0x80) != 0

    return MachineState(proc, mem)

instruction_table = {
    0x18: Instruction("CLC", ins_clc_imp, 1),
    0x38: Instruction("SEC", ins_sec_imp, 1),
    0xEA: Instruction("NOP", ins_nop_imp, 1),
    0xAA: Instruction("TAX", ins_tax_imp, 1),
    0xE8: Instruction("INX", ins_inx_imp, 1),
    0xA9: Instruction("LDA", ins_lda_imm, 0)
}
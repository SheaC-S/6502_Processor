from dataclasses import dataclass
from dis import Instruction
from typing import Callable

from processor import Processor, MachineState
from memory import Memory


@dataclass
class Instruction:
    name: str
    execute: Callable
    cycles: int
    pattern: str # For the string pattern which will be used for this instruction



instruction_table = {
    0x18: Instruction("CLC", ins_clc_imp, 1),
    0x38: Instruction("SEC", ins_sec_imp, 1),
    0xEA: Instruction("NOP", ins_nop_imp, 1),
    0xAA: Instruction("TAX", ins_tax_imp, 1),
    0xE8: Instruction("INX", ins_inx_imp, 1),
    0xA9: Instruction("LDA", ins_lda_imm, 0)
}

def ins_clc_imp(state: MachineState) -> MachineState:
    """
    CLC - Clear Carry Flag.

    :return: None
    """
    proc: Processor = state.cpu
    mem: Memory = state.memory

    proc.flag_c = False

    return MachineState(proc, mem)

def ins_sec_imp(proc : 'Processor') -> None:
    """
    SEC - Set Carry Flag.

    :return: None
    """
    proc.flag_c = True

    return None

def ins_nop_imp(proc : 'Processor') -> None:
    """
    NOP - No Operation.

    :return: None
    """

    return None

def ins_tax_imp(proc : 'Processor') -> None:
    """
    TAX - Transfer Accumulator to X.

    :return: None
    """
    proc.reg_x = proc.reg_a
    proc.flag_z = (proc.reg_x == 0)
    proc.flag_n = (proc.reg_x & 0x80) != 0

def ins_inx_imp(proc : 'Processor') -> None:
    """
    INX - Increment X Register.

    :return: None
    """
    proc.reg_x = (proc.reg_x + 1) & 0xFF
    proc.flag_z = (proc.reg_x == 0)
    proc.flag_n = (proc.reg_x & 0x80) != 0

def ins_lda_imm(proc : 'Processor') -> None:
    """
    LDA - Load to Accumulator.

    :return: None
    """
    proc.reg_a = proc.fetch_byte()
    proc.flag_z = (proc.reg_a == 0)
    proc.flag_n = (proc.reg_a & 0x80) != 0
from memory import Memory
from instructions import instruction_table
import sys

from dataclasses import dataclass


"""
Code review of this before next week


Justify choices made in terms of the design / implementation of it so far - 
    we can then discuss possible improvements next week 
"""



@dataclass
class ProcessorState:
    reg_a: int
    reg_b: int
    reg_x: int
    program_counter: int
    stack_pointer: int
    cycles: int
    flag_c: bool  # Carry
    flag_z: bool  # Zero
    flag_i: bool  # Interrupt disable
    flag_d: bool  # Decimal mode
    flag_b: bool  # Break
    flag_v: bool  # Overflow
    flag_n: bool  # Negative result

@dataclass
class MachineState:
    cpu: ProcessorState
    memory: Memory
"""

Data:
InstructionLabel X OpCode
= {
    (NOP, 
}
Behaviour:
Execute: State -> State


"""

'''class InstructionEnum:
    NOP =0x00


    @staticmethod
    def execute(instr:InstructionEnum, st:State) -> State:
        match instr:
            case 0x00:
                NOP.execute()

class NOP:
        op_code = 0x00

        @staticmethod
        def execute(proc:Processor, mem:Memory) -> Tuple[Processor, Memory]:

'''

class Processor:
    def __init__(proc : 'Processor', memory: Memory) -> None:
        """
        Initialise the processor

        :return: none
        """
        proc.reg_a = 0 # Accumulator
        proc.reg_b = 0
        proc.reg_x = 0

        proc.program_counter = 0
        proc.stack_pointer = 0
        proc.cycles = 0

        proc.flag_c = True  # Carry
        proc.flag_z = True  # Zero
        proc.flag_i = True  # Interrupt disable
        proc.flag_d = True  # Decimal mode
        proc.flag_b = True  # Break
        proc.flag_v = True  # Overflow
        proc.flag_n = True  # Negative result

        proc.instruction_table = instruction_table

    def reset(proc : 'Processor') -> None:

        proc.program_counter = 0xFCE2
        proc.stack_pointer = 0x01FD
        proc.cycles = 0
        proc.flag_i = True
        proc.flag_d = False
        proc.flag_b = True

    def read_byte(proc : 'Processor', address: int) -> int:
        """Read a byte from memory.

        :param address: The address to read from
        :return: int
        """
        data = proc.memory[address]
        proc.cycles += 1
        return data

    def write_byte(proc : 'Processor', address: int, value: int) -> None:
        """Write a byte to memory.

        :param address: The address to write to
        :param value: The value to write
        :return: None
        """
        proc.memory[address] = value
        proc.cycles += 1

    def read_word(proc : 'Processor', address: int) -> int:
        """Read a word from memory.

        :param address: The address to read from
        :return: int
        """
        if sys.byteorder == "little":
            data = proc.read_byte(address) | (proc.read_byte(address + 1) << 8)
        else:
            data = (proc.read_byte(address) << 8) | proc.read_byte(address + 1)
        return data


    def write_word(proc : 'Processor', address: int, value: int) -> None:
        """Split a word to two bytes and write to memory.

        :param address: The address to write to
        :param value: The value to write
        :return: None
        """
        if sys.byteorder == "little":
            proc.write_byte(address, value & 0xFF)
            proc.write_byte(address + 1, (value >> 8) & 0xFF)
        else:
            proc.write_byte(address, (value >> 8) & 0xFF)
            proc.write_byte(address + 1, value & 0xFF)

    def fetch_byte(proc : 'Processor') -> int:
        """Fetch a byte from memory.

        :param address: The address to read from
        :return: int
        """
        data = proc.read_byte(proc.program_counter)
        proc.program_counter += 1
        return data

    def fetch_word(proc : 'Processor') -> int:
        """Fetch a word from memory.

        :param address: The address to read from
        :return: int
        """
        data = proc.read_word(proc.program_counter)
        proc.program_counter += 2
        return data

    def fetch_decode_execute(state : MachineState) -> None:
        opcode = proc.fetch_byte()
        instruction = proc.decode(opcode)
        proc.execute(instruction)

    def decode(state : MachineState, opcode: int) -> Instruction:
        proc = state.cpu
        memory = state.memory

        try:
            ins  = proc.instruction_table.get(opcode, None)
            if ins == None:
                raise ValueError(f"Unknown opcode: {opcode} at PC={proc.program_counter}. Running No Operation...")
        except ValueError:
            return proc.instruction_table.get(0xEA)
        return ins

    def execute(proc : 'Processor', instruction) -> None:
        """
        Execute code for X amount of cycles. Or until a breakpoint is reached.

        :param cycles: The number of cycles to execute
        :return: None
        """
        instruction.execute(proc)
        proc.cycles += instruction.cycles

        '''
        while (self.cycles < cycles) or (cycles == 0):
            opcode = self.fetch_byte()
            # you have a multiway branch use a match expression
            if opcode == 0x18:
                self.ins_clc_imp()  # Clear carry flag
            elif opcode == 0x38:
                self.ins_sec_imp()  # Set carry flag
            elif opcode == 0xEA:
                self.ins_nop_imp()  # No operation
            elif opcode == 0xAA:
                self.ins_tax_imp()  # Transfer ACC to reg X
            elif opcode == 0xE8:
                self.ins_inx_imp()  # Increment reg X
            elif opcode == 0xA9:
                self.ins_lda_imm()  # Load value to ACC
            else:
                print("Unknown Opcode")
                break
            ...
        '''



from memory import Memory
from instructions import instruction_table, Instruction
from state import MachineState
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
    def __init__(proc : 'Processor') -> None:
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
        proc.flag_d = False  # Decimal mode
        proc.flag_b = True  # Break
        proc.flag_v = True  # Overflow
        proc.flag_n = True  # Negative result

        proc.instruction_table = instruction_table

    def reset(proc : 'Processor') -> None:

        proc.reg_a = 0
        proc.reg_b = 0
        proc.reg_x = 0

        proc.program_counter = 0x0200
        proc.stack_pointer = 0x0100
        proc.cycles = 0

        proc.flag_c = False
        proc.flag_z = False
        proc.flag_i = True
        proc.flag_d = False
        proc.flag_b = False
        proc.flag_v = False
        proc.flag_n = False

    def read_byte(proc : 'Processor', mem : Memory, address: int) -> int:
        """Read a byte from memory.

        :param address: The address to read from
        :return: int
        """
        data = mem[address]
        proc.cycles += 1
        return data

    def write_byte(proc : 'Processor', mem : Memory, address: int, value: int) -> None:
        """Write a byte to memory.

        :param address: The address to write to
        :param value: The value to write
        :return: None
        """
        mem[address] = value
        proc.cycles += 1

    def read_word(proc : 'Processor', mem : Memory, address: int) -> int:
        """Read a word from memory.

        :param address: The address to read from
        :return: int
        """
        if sys.byteorder == "little":
            data = proc.read_byte(mem, address) | (proc.read_byte(mem, address + 1) << 8)
        else:
            data = (proc.read_byte(mem, address) << 8) | proc.read_byte(mem, address + 1)
        return data


    def write_word(proc : 'Processor', mem : Memory, address: int, value: int) -> None:
        """Split a word to two bytes and write to memory.

        :param address: The address to write to
        :param value: The value to write
        :return: None
        """
        if sys.byteorder == "little":
            proc.write_byte(mem, address, value & 0xFF)
            proc.write_byte(mem, address + 1, (value >> 8) & 0xFF)
        else:
            proc.write_byte(mem, address, (value >> 8) & 0xFF)
            proc.write_byte(mem, address + 1, value & 0xFF)

    def fetch_byte(proc : 'Processor', mem : Memory) -> int:
        """Fetch a byte from memory.

        :param address: The address to read from
        :return: int
        """
        data = proc.read_byte(mem, proc.program_counter)
        # proc.program_counter += 1
        proc.program_counter = (proc.program_counter + 1) % 0x10000
        return data

    def fetch_word(proc : 'Processor', mem : Memory) -> int:
        """Fetch a word from memory.

        :param address: The address to read from
        :return: int
        """
        data = proc.read_word(mem, proc.program_counter)
        # proc.program_counter += 2
        proc.program_counter = (proc.program_counter + 2) % 0x10000
        return data

    def fetch_decode_execute(self, state : MachineState) -> None:
        proc: "Processor" = state.cpu
        mem: "Memory" = state.memory

        opcode = proc.fetch_byte(mem)
        instruction = proc.decode(opcode)
        proc.execute(state, instruction)

    def decode(proc: 'Processor', opcode : int) -> Instruction:
        try:
            instruction  = instruction_table.get(opcode, None)
            if instruction == None:
                raise ValueError(f"Unknown opcode. Running No Operation...")
        except ValueError:
            return instruction_table.get(0xEA)
        return instruction

    def execute(proc : 'Processor', state: MachineState, instruction) -> None:
        """
        Execute code for X amount of cycles. Or until a breakpoint is reached.

        :param cycles: The number of cycles to execute
        :return: None
        """
        state = instruction.execute(state)
        state.cpu.cycles += instruction.cycles



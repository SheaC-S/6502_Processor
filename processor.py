from memory import Memory
import sys


"""
Code review of this before next week


Justify choices made in terms of the design / implementation of it so far - 
    we can then discuss possible improvements next week 
"""

class Processor:
    def __init__(self, memory: Memory) -> None:
        """
        Initialise the processor

        :return: none
        """
        self.memory = memory
        self.reg_a = 0
        self.reg_b = 0
        self.reg_x = 0

        self.program_counter = 0
        self.stack_pointer = 0
        self.cycles = 0

        self.flag_c = True # Carry
        self.flag_z = True # Zero
        self.flag_i = True #
        self.flag_d = True
        self.flag_b = True
        self.flag_v = True
        self.flag_n = True

    def reset(self) -> None:

        self.program_counter = 0xFCE2
        self.stack_pointer = 0x01FD
        self.cycles = 0
        self.flag_i = True
        self.flag_d = False
        self.flag_b = True

    def read_byte(self, address: int) -> int:
        """Read a byte from memory.

        :param address: The address to read from
        :return: int
        """
        data = self.memory[address]
        self.cycles += 1
        return data

    def write_byte(self, address: int, value: int) -> None:
        """Write a byte to memory.

        :param address: The address to write to
        :param value: The value to write
        :return: None
        """
        self.memory[address] = value
        self.cycles += 1

    def read_word(self, address: int) -> int:
        """Read a word from memory.

        :param address: The address to read from
        :return: int
        """
        if sys.byteorder == "little":
            data = self.read_byte(address) | (self.read_byte(address + 1) << 8)
        else:
            data = (self.read_byte(address) << 8) | self.read_byte(address + 1)
        return data


    def write_word(self, address: int, value: int) -> None:
        """Split a word to two bytes and write to memory.

        :param address: The address to write to
        :param value: The value to write
        :return: None
        """
        if sys.byteorder == "little":
            self.write_byte(address, value & 0xFF)
            self.write_byte(address + 1, (value >> 8) & 0xFF)
        else:
            self.write_byte(address, (value >> 8) & 0xFF)
            self.write_byte(address + 1, value & 0xFF)

    def fetch_byte(self) -> int:
        """Fetch a byte from memory.

        :param address: The address to read from
        :return: int
        """
        data = self.read_byte(self.program_counter)
        self.program_counter += 1
        return data


    def fetch_word(self) -> int:
        """Fetch a word from memory.

        :param address: The address to read from
        :return: int
        """
        data = self.read_word(self.program_counter)
        self.program_counter += 2
        return data

    def execute(self, cycles: int = 0) -> None:
        """
        Execute code for X amount of cycles. Or until a breakpoint is reached.

        :param cycles: The number of cycles to execute
        :return: None
        """
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



    def ins_clc_imp(self) -> None:
        """
        CLC - Clear Carry Flag.

        :return: None
        """
        self.flag_c = False
        self.cycles += 1

    def ins_sec_imp(self) -> None:
        """
        SEC - Set Carry Flag.

        :return: None
        """
        self.flag_c = True
        self.cycles += 1

    def ins_nop_imp(self) -> None:
        """
        NOP - No Operation.

        :return: None
        """
        self.cycles += 1

    def ins_tax_imp(self) -> None:
        """
        TAX - Transfer Accumulator to X.

        :return: None
        """
        self.reg_x = self.reg_a
        self.flag_z = (self.reg_x == 0)
        self.flag_n = (self.reg_x & 0x80) != 0
        self.cycles += 1

    def ins_inx_imp(self) -> None:
        """
        INX - Increment X Register.

        :return: None
        """
        self.reg_x = (self.reg_x + 1) & 0xFF
        self.flag_z = (self.reg_x == 0)
        self.flag_n = (self.reg_x & 0x80) != 0
        self.cycles += 1

    def ins_lda_imm(self) -> None:
        """
        LDA - Load to Accumulator.

        :return: None
        """
        self.reg_a = self.fetch_byte()
        self.flag_z = (self.reg_a == 0)
        self.flag_n = (self.reg_a & 0x80) != 0
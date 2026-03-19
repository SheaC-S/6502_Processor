import pytest
from memory import Memory
from processor import Processor

@pytest.mark.parametrize("i", range(0x0000, 0x0100))
def test_write_zero_page(i: int) -> None:
    """Verify that the Zero-Page memory can be written to and
    read from.

    :param i: The address to write to
    :return: None
    """
    memory = Memory()
    memory[i] = 0xA5
    assert memory[i] == 0xA5

@pytest.mark.parametrize("i", range(0x0100, 0x0200))
def test_write_stack(i: int) -> None:
    """Verify that the Stack memory can be written to and
    read from.

    :param i: The address to write to
    :return: None
    """
    memory = Memory()
    memory[i] = 0xA5
    assert memory[i] == 0xA5

@pytest.mark.parametrize("i", [0xFFFC, 0xFFFD])
def test_write_vector(i: int) -> None:
    """Verify that the C64 vector memory can be written to and
    read from.

    :param i: The address to write to
    :return: None
    """
    memory = Memory()
    memory[i] = 0xA5
    assert memory[i] == 0xA5

def test_cpu_read_write_byte() -> None:
    """Verify CPU can read and write a byte from memory.

    The is 1 cycle each
    The state of the CPU is not changed.

    :return: None
    """
    memory = Memory()
    cpu = Processor(memory)
    cpu.reset()
    cpu.write_byte(0x0001, 0xA5)
    value = cpu.read_byte(0x0001)
    assert (
               cpu.program_counter,
               cpu.stack_pointer,
               cpu.cycles,
               cpu.flag_b,
               cpu.flag_d,
               cpu.flag_i,
               value,
           ) == (0xFCE2, 0x01FD, 2, True, False, True, 0xA5)

def test_cpu_read_write_word() -> None:
    """Verify CPU can read and write a byte from memory.

    The cost is 2 cycles each.
    The state of the CPU is not changed.

    :return: None
    """
    memory = Memory()
    cpu = Processor(memory)
    cpu.reset()
    cpu.write_word(0x0001, 0x5AA5)
    value = cpu.read_word(0x0001)
    assert (
        cpu.program_counter,
        cpu.stack_pointer,
        cpu.cycles,
        cpu.flag_b,
        cpu.flag_d,
        cpu.flag_i,
        value,
    ) == (0xFCE2, 0x01FD, 4, True, False, True, 0x5AA5)

def test_cpu_fetch_byte() -> None:
    """Verify CPU can fetch a byte from memory.

    The cost is 1 cycle, and increases the program counter by 1.
    The state of the CPU is not changed further.

    :return: None
    """
    memory = Memory()
    cpu = Processor(memory)
    cpu.reset()
    memory[0xFCE2] = 0xA5
    value = cpu.fetch_byte()
    assert (
               cpu.program_counter,
               cpu.stack_pointer,
               cpu.cycles,
               cpu.flag_b,
               cpu.flag_d,
               cpu.flag_i,
               value,
           ) == (0xFCE3, 0x01FD, 1, True, False, True, 0xA5)

def test_cpu_fetch_word() -> None:
    """Verify CPU can fetch a word from memory.

    The cost is 2 cycles and increases the program counter by 2.
    The state of the CPU is not changed further.

    :return: None
    """
    memory = Memory()
    cpu = Processor(memory)
    cpu.reset()
    memory[0xFCE2] = 0xA5
    memory[0xFCE3] = 0x5A
    value = cpu.fetch_word()
    assert (
               cpu.program_counter,
               cpu.stack_pointer,
               cpu.cycles,
               cpu.flag_b,
               cpu.flag_d,
               cpu.flag_i,
               value,
           ) == (0xFCE4, 0x01FD, 2, True, False, True, 0x5AA5)



def test_cpu_ins_sec() -> None:
    """Verify SEC (Set Carry Flag) instruction.

    The cost is 2 cycles.
    Sets the carry flag to True.

    :return: None
    """
    memory = Memory()
    cpu = Processor(memory)
    cpu.reset()
    cpu.flag_c = False

    memory[0xFCE2] = 0x38
    cpu.execute(2)

    assert (
            cpu.flag_c,
            cpu.cycles,
            cpu.program_counter
           ) == (True, 2, 0xFCE3)

def test_cpu_ins_tax() -> None:
    """Verify TAX (Transfer A to X) instruction.

    The cost is 2 cycles. It transfers the value of the Accumulator
    to the X register and updates the Zero and Negative flags.
    """
    memory = Memory()
    cpu = Processor(memory)
    cpu.reset()

    cpu.reg_a = 0x64
    cpu.reg_x = 0x00

    memory[0xFCE2] = 0xAA
    cpu.execute(2)

    assert (
            cpu.reg_x,
            cpu.flag_z,
            cpu.flag_n,
            cpu.cycles,
            cpu.program_counter
    ) == (0x64, False, False, 2, 0xFCE3)

def test_cpu_ins_inx_standard() -> None:
    """Verify INX (Increment X) instruction standard operation.

    The cost is 2 cycles. It increments the X register by 1.
    """
    memory = Memory()
    cpu = Processor(memory)
    cpu.reset()

    cpu.reg_x = 0x05

    memory[0xFCE2] = 0xE8
    cpu.execute(2)

    assert  (
            cpu.reg_x,
            cpu.flag_z,
            cpu.flag_n,
            cpu.cycles,
            cpu.program_counter
    ) == (0x06, False, False, 2, 0xFCE3)

def test_cpu_ins_inx_overflow_and_flags() -> None:
    """Verify INX correctly wraps around at 255 and sets flags.

    When incrementing 255 (0xFF), it should wrap to 0x00 and trigger
    the Zero flag.
    """
    memory = Memory()
    cpu = Processor(memory)
    cpu.reset()

    cpu.reg_x = 0xFF

    memory[0xFCE2] = 0xE8
    cpu.execute(2)

    assert (
        cpu.reg_x,
        cpu.flag_z,
        cpu.flag_n,
        cpu.cycles,
        cpu.program_counter
    ) == (0x00, True, False, 2, 0xFCE3)

def test_cpu_ins_lda_imm() -> None:
    """Verify LDA instruction.

    The cost is 2 cycles.
    It loads the byte immediately following the opcode into
    the Accumulator and updates flags.
    """
    memory = Memory()
    cpu = Processor(memory)
    cpu.reset()

    memory[0xFCE2] = 0xA9
    memory[0xFCE3] = 0x84

    cpu.execute(2)

    assert (
        cpu.reg_a,
        cpu.flag_n,
        cpu.flag_z,
        cpu.cycles,
        cpu.program_counter
    ) == (0x84, True, False, 2, 0xFCE4)



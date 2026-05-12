import pytest
from memory import Memory
from processor import Processor
from state import MachineState


@pytest.fixture(scope="module")
def newMachine() -> MachineState:
    """Have a single machine to use for all tests, rather than just creating new ones each time.

    :return: a new MachineState tuple
    """
    cpu = Processor()
    memory = Memory(0x1FFFF)
    return MachineState(cpu=cpu, memory=memory)

@pytest.fixture(scope="function")
def machineReset(newMachine : MachineState) -> MachineState:
    """
    :param state: The MachineState to use for testing

    :return: a reset MachineState, ready for the next test
    """
    processor = newMachine.cpu
    memory = newMachine.memory

    processor.reset()
    memory.memory = [0] * memory.size

    return MachineState(cpu=processor, memory=memory)


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

def test_cpu_read_write_byte(machineReset: MachineState) -> None:
    """Verify CPU can read and write a byte from memory.

    Cycles remain 0 because raw memory operations no longer increment cycles.
    The state of the CPU is not changed.

    :return: None
    """
    memory = machineReset.memory
    cpu = machineReset.cpu

    cpu.write_byte(memory, 0x0200, 0xA5)
    value = cpu.read_byte(memory, 0x0200)

    assert (
               cpu.program_counter,
               cpu.stack_pointer,
               cpu.cycles,
               cpu.flag_b,
               cpu.flag_d,
               cpu.flag_i,
               value,
           ) == (0x0200, 0xFF, 0, False, False, True, 0xA5)


def test_cpu_read_write_word(machineReset: MachineState) -> None:
    """Verify CPU can read and write a word from memory.

    Cycles remain 0 because raw memory operations no longer increment cycles.
    The state of the CPU is not changed.

    :return: None
    """
    memory = machineReset.memory
    cpu = machineReset.cpu

    cpu.write_word(memory, 0x0001, 0x5AA5)
    value = cpu.read_word(memory, 0x0001)

    assert (
               cpu.program_counter,
               cpu.stack_pointer,
               cpu.cycles,
               cpu.flag_b,
               cpu.flag_d,
               cpu.flag_i,
               value,
           ) == (0x0200, 0xFF, 0, False, False, True, 0x5AA5)


def test_cpu_fetch_byte(machineReset: MachineState) -> None:
    """Verify CPU can fetch a byte from memory.

    Increases the program counter by 1.
    Cycles remain 0 because they are handled in execute().

    :return: None
    """
    memory = machineReset.memory
    cpu = machineReset.cpu

    # Explicitly move PC to the test address
    cpu.program_counter = 0xBCE2

    memory[0xBCE2] = 0xA5
    value = cpu.fetch_byte(memory)

    assert (
               cpu.program_counter,
               cpu.stack_pointer,
               cpu.cycles,
               cpu.flag_b,
               cpu.flag_d,
               cpu.flag_i,
               value,
           ) == (0xBCE3, 0xFF, 0, False, False, True, 0xA5)


def test_cpu_fetch_word(machineReset: MachineState) -> None:
    """Verify CPU can fetch a word from memory.

    Increases the program counter by 2.
    Cycles remain 0 because they are handled in execute().

    :return: None
    """
    memory = machineReset.memory
    cpu = machineReset.cpu

    # Explicitly move PC to the test address
    cpu.program_counter = 0xBCE2

    memory[0xBCE2] = 0xA5
    memory[0xBCE3] = 0x5A
    value = cpu.fetch_word(memory)

    assert (
               cpu.program_counter,
               cpu.stack_pointer,
               cpu.cycles,
               cpu.flag_b,
               cpu.flag_d,
               cpu.flag_i,
               value,
           ) == (0xBCE4, 0xFF, 0, False, False, True, 0x5AA5)


def test_cpu_ins_sec(machineReset: MachineState) -> None:
    """Verify SEC (Set Carry Flag) instruction.

    The cost is 2 cycles.
    Sets the carry flag to True.

    :return: None
    """
    memory = machineReset.memory
    cpu = machineReset.cpu

    cpu.program_counter = 0xBCE2
    cpu.flag_c = False

    memory[0xBCE2] = 0x38
    machineState = MachineState(cpu=cpu, memory=memory)
    cpu.fetch_decode_execute(machineState)

    assert (
               cpu.flag_c,
               cpu.cycles,
               cpu.program_counter
           ) == (True, 2, 0xBCE3)


def test_cpu_ins_tax(machineReset: MachineState) -> None:
    """Verify TAX (Transfer A to X) instruction.

    The cost is 2 cycles. It transfers the value of the Accumulator
    to the X register and updates the Zero and Negative flags.
    """
    memory = machineReset.memory
    cpu = machineReset.cpu

    cpu.program_counter = 0xBCE2
    cpu.reg_a = 0x64
    cpu.reg_x = 0x00

    memory[0xBCE2] = 0xAA
    machineState = MachineState(cpu=cpu, memory=memory)
    cpu.fetch_decode_execute(machineState)

    assert (
               cpu.reg_x,
               cpu.flag_z,
               cpu.flag_n,
               cpu.cycles,
               cpu.program_counter
           ) == (0x64, False, False, 2, 0xBCE3)


def test_cpu_ins_inx_standard(machineReset: MachineState) -> None:
    """Verify INX (Increment X) instruction standard operation.

    The cost is 2 cycles. It increments the X register by 1.
    """
    memory = machineReset.memory
    cpu = machineReset.cpu

    cpu.program_counter = 0xBCE2
    cpu.reg_x = 0x05

    memory[0xBCE2] = 0xE8
    machineState = MachineState(cpu=cpu, memory=memory)
    cpu.fetch_decode_execute(machineState)

    assert (
               cpu.reg_x,
               cpu.flag_z,
               cpu.flag_n,
               cpu.cycles,
               cpu.program_counter
           ) == (0x06, False, False, 2, 0xBCE3)


def test_cpu_ins_inx_overflow_and_flags(machineReset: MachineState) -> None:
    """Verify INX correctly wraps around at 255 and sets flags.

    When incrementing 255 (0xFF), it should wrap to 0x00 and trigger
    the Zero flag.
    """
    memory = machineReset.memory
    cpu = machineReset.cpu

    cpu.program_counter = 0xBCE2
    cpu.reg_x = 0xFF

    memory[0xBCE2] = 0xE8
    machineState = MachineState(cpu=cpu, memory=memory)
    cpu.fetch_decode_execute(machineState)

    assert (
               cpu.reg_x,
               cpu.flag_z,
               cpu.flag_n,
               cpu.cycles,
               cpu.program_counter
           ) == (0x00, True, False, 2, 0xBCE3)


def test_cpu_ins_lda_imm(machineReset: MachineState) -> None:
    """Verify LDA instruction.

    The cost is 2 cycles.
    It loads the byte immediately following the opcode into
    the Accumulator and updates flags.
    """
    memory = machineReset.memory
    cpu = machineReset.cpu

    cpu.program_counter = 0xBCE2
    memory[0xBCE2] = 0xA9
    memory[0xBCE3] = 0x84

    machineState = MachineState(cpu=cpu, memory=memory)
    cpu.fetch_decode_execute(machineState)

    assert (
               cpu.reg_a,
               cpu.flag_n,
               cpu.flag_z,
               cpu.cycles,
               cpu.program_counter
           ) == (0x84, True, False, 2, 0xBCE4)


# ==========================================
# REGISTER TRANSFERS
# ==========================================

def test_cpu_ins_tay(machineReset: MachineState) -> None:
    cpu, mem = machineReset.cpu, machineReset.memory
    cpu.program_counter = 0xBCE2
    cpu.reg_a = 0x55
    mem[0xBCE2] = 0xA8  # TAY
    cpu.fetch_decode_execute(machineReset)
    assert cpu.reg_y == 0x55 and not cpu.flag_z and not cpu.flag_n


def test_cpu_ins_txa(machineReset: MachineState) -> None:
    cpu, mem = machineReset.cpu, machineReset.memory
    cpu.program_counter = 0xBCE2
    cpu.reg_x = 0x00
    mem[0xBCE2] = 0x8A  # TXA
    cpu.fetch_decode_execute(machineReset)
    assert cpu.reg_a == 0x00 and cpu.flag_z and not cpu.flag_n


def test_cpu_ins_tya(machineReset: MachineState) -> None:
    cpu, mem = machineReset.cpu, machineReset.memory
    cpu.program_counter = 0xBCE2
    cpu.reg_y = 0x80
    mem[0xBCE2] = 0x98  # TYA
    cpu.fetch_decode_execute(machineReset)
    assert cpu.reg_a == 0x80 and not cpu.flag_z and cpu.flag_n


def test_cpu_ins_txs_tsx(machineReset: MachineState) -> None:
    cpu, mem = machineReset.cpu, machineReset.memory
    cpu.program_counter = 0xBCE2
    cpu.reg_x = 0xAA
    mem[0xBCE2] = 0x9A  # TXS
    mem[0xBCE3] = 0xBA  # TSX
    cpu.fetch_decode_execute(machineReset)  # Execute TXS
    assert cpu.stack_pointer == 0xAA
    cpu.reg_x = 0x00  # Clear X to prove TSX works
    cpu.fetch_decode_execute(machineReset)  # Execute TSX
    assert cpu.reg_x == 0xAA


# ==========================================
# LOAD AND STORE
# ==========================================

def test_cpu_ins_ldx_ldy_imm(machineReset: MachineState) -> None:
    cpu, mem = machineReset.cpu, machineReset.memory
    cpu.program_counter = 0xBCE2
    mem[0xBCE2] = 0xA2  # LDX Imm
    mem[0xBCE3] = 0x11
    mem[0xBCE4] = 0xA0  # LDY Imm
    mem[0xBCE5] = 0x22
    cpu.fetch_decode_execute(machineReset)
    cpu.fetch_decode_execute(machineReset)
    assert cpu.reg_x == 0x11 and cpu.reg_y == 0x22


def test_cpu_ins_sta_stx_sty_zp(machineReset: MachineState) -> None:
    cpu, mem = machineReset.cpu, machineReset.memory
    cpu.program_counter = 0xBCE2
    cpu.reg_a, cpu.reg_x, cpu.reg_y = 0x11, 0x22, 0x33
    mem[0xBCE2] = 0x85  # STA ZP
    mem[0xBCE3] = 0x10
    mem[0xBCE4] = 0x86  # STX ZP
    mem[0xBCE5] = 0x11
    mem[0xBCE6] = 0x84  # STY ZP
    mem[0xBCE7] = 0x12
    cpu.fetch_decode_execute(machineReset)
    cpu.fetch_decode_execute(machineReset)
    cpu.fetch_decode_execute(machineReset)
    assert mem[0x10] == 0x11 and mem[0x11] == 0x22 and mem[0x12] == 0x33


# ==========================================
# STACK OPERATIONS
# ==========================================

def test_cpu_ins_pha_pla(machineReset: MachineState) -> None:
    cpu, mem = machineReset.cpu, machineReset.memory
    cpu.program_counter = 0xBCE2
    cpu.reg_a = 0x99
    mem[0xBCE2] = 0x48  # PHA
    mem[0xBCE3] = 0x68  # PLA
    cpu.fetch_decode_execute(machineReset)  # Push
    assert mem[0x01FF] == 0x99
    assert cpu.stack_pointer == 0xFE
    cpu.reg_a = 0x00  # Clear A
    cpu.fetch_decode_execute(machineReset)  # Pop
    assert cpu.reg_a == 0x99
    assert cpu.stack_pointer == 0xFF


def ins_php(state: MachineState, address: int) -> MachineState:
    """PHP - Push Processor Status"""
    proc = state.cpu
    mem = state.memory

    # Pack the boolean flags into a single 8-bit integer
    status = 0
    if proc.flag_c: status |= 0b00000001
    if proc.flag_z: status |= 0b00000010
    if proc.flag_i: status |= 0b00000100
    if proc.flag_d: status |= 0b00001000
    if proc.flag_b: status |= 0b00010000
    status |= 0b00100000  # Bit 5 is unused but is always pushed as 1 by the 6502
    if proc.flag_v: status |= 0b01000000
    if proc.flag_n: status |= 0b10000000

    proc.push_byte(mem, status)
    return state


def ins_plp(state: MachineState, address: int) -> MachineState:
    """PLP - Pull Processor Status"""
    proc = state.cpu
    mem = state.memory

    # Pop the byte and unpack it back into the boolean flags
    status = proc.pop_byte(mem)

    proc.flag_c = bool(status & 0b00000001)
    proc.flag_z = bool(status & 0b00000010)
    proc.flag_i = bool(status & 0b00000100)
    proc.flag_d = bool(status & 0b00001000)
    # Note: PLP typically ignores the Break flag (Bit 4), but we'll set it for completeness
    proc.flag_b = bool(status & 0b00010000)
    proc.flag_v = bool(status & 0b01000000)
    proc.flag_n = bool(status & 0b10000000)

    return state


# ==========================================
# ALU & MATH (ADC, SBC, AND, ORA, EOR, CMP)
# ==========================================

def test_cpu_ins_adc_imm(machineReset: MachineState) -> None:
    cpu, mem = machineReset.cpu, machineReset.memory
    cpu.program_counter = 0xBCE2
    cpu.reg_a = 0x50
    cpu.flag_c = False
    mem[0xBCE2] = 0x69  # ADC Imm
    mem[0xBCE3] = 0x50
    cpu.fetch_decode_execute(machineReset)
    # 0x50 + 0x50 = 0xA0 (160), no carry, but negative flag set
    assert cpu.reg_a == 0xA0 and not cpu.flag_c and cpu.flag_n


def test_cpu_ins_sbc_imm(machineReset: MachineState) -> None:
    cpu, mem = machineReset.cpu, machineReset.memory
    cpu.program_counter = 0xBCE2
    cpu.reg_a = 0x50
    cpu.flag_c = True  # Carry means NO borrow in 6502
    mem[0xBCE2] = 0xE9  # SBC Imm
    mem[0xBCE3] = 0x30
    cpu.fetch_decode_execute(machineReset)
    assert cpu.reg_a == 0x20 and cpu.flag_c


def test_cpu_ins_and_ora_eor(machineReset: MachineState) -> None:
    cpu, mem = machineReset.cpu, machineReset.memory
    cpu.program_counter = 0xBCE2
    cpu.reg_a = 0b11001100
    mem[0xBCE2] = 0x29  # AND
    mem[0xBCE3] = 0b10101010  # Result: 0b10001000
    mem[0xBCE4] = 0x09  # ORA
    mem[0xBCE5] = 0b00000111  # Result: 0b10001111
    mem[0xBCE6] = 0x49  # EOR
    mem[0xBCE7] = 0b11111111  # Result: 0b01110000
    cpu.fetch_decode_execute(machineReset)
    assert cpu.reg_a == 0b10001000
    cpu.fetch_decode_execute(machineReset)
    assert cpu.reg_a == 0b10001111
    cpu.fetch_decode_execute(machineReset)
    assert cpu.reg_a == 0b01110000


def test_cpu_ins_cmp_cpx_cpy(machineReset: MachineState) -> None:
    cpu, mem = machineReset.cpu, machineReset.memory
    cpu.program_counter = 0xBCE2
    cpu.reg_a, cpu.reg_x, cpu.reg_y = 0x10, 0x20, 0x30
    mem[0xBCE2] = 0xC9  # CMP Imm
    mem[0xBCE3] = 0x10  # A == 0x10 (Zero set, Carry set)
    mem[0xBCE4] = 0xE0  # CPX Imm
    mem[0xBCE5] = 0x25  # X < 0x25 (Carry clear, Neg set)
    mem[0xBCE6] = 0xC0  # CPY Imm
    mem[0xBCE7] = 0x25  # Y > 0x25 (Carry set, Zero clear)

    cpu.fetch_decode_execute(machineReset)
    assert cpu.flag_z and cpu.flag_c
    cpu.fetch_decode_execute(machineReset)
    assert not cpu.flag_c and cpu.flag_n
    cpu.fetch_decode_execute(machineReset)
    assert cpu.flag_c and not cpu.flag_z


def test_cpu_ins_bit_zp(machineReset: MachineState) -> None:
    cpu, mem = machineReset.cpu, machineReset.memory
    cpu.program_counter = 0xBCE2
    cpu.reg_a = 0b00001111
    mem[0x10] = 0b11000000  # Memory has bit 7 and 6 set, no overlap with A
    mem[0xBCE2] = 0x24  # BIT ZP
    mem[0xBCE3] = 0x10
    cpu.fetch_decode_execute(machineReset)
    assert cpu.flag_z and cpu.flag_n and cpu.flag_v


# ==========================================
# INCREMENTS & DECREMENTS
# ==========================================

def test_cpu_ins_inc_dec_zp(machineReset: MachineState) -> None:
    cpu, mem = machineReset.cpu, machineReset.memory
    cpu.program_counter = 0xBCE2
    mem[0x10] = 0x00
    mem[0xBCE2] = 0xE6  # INC ZP
    mem[0xBCE3] = 0x10
    mem[0xBCE4] = 0xC6  # DEC ZP
    mem[0xBCE5] = 0x10
    cpu.fetch_decode_execute(machineReset)
    assert mem[0x10] == 0x00


def test_cpu_ins_dey(machineReset: MachineState) -> None:
    cpu, mem = machineReset.cpu, machineReset.memory
    cpu.program_counter = 0xBCE2
    cpu.reg_y = 0x00
    mem[0xBCE2] = 0x88  # DEY
    cpu.fetch_decode_execute(machineReset)
    assert cpu.reg_y == 0xFF and cpu.flag_n


def test_cpu_ins_iny(machineReset: MachineState) -> None:
    cpu, mem = machineReset.cpu, machineReset.memory
    cpu.program_counter = 0xBCE2
    cpu.reg_y = 0x05
    mem[0xBCE2] = 0xC8  # INY
    cpu.fetch_decode_execute(machineReset)
    assert cpu.reg_y == 0x06


# ==========================================
# SHIFTS (ASL, LSR, ROL, ROR)
# ==========================================

def test_cpu_ins_asl_lsr_acc(machineReset: MachineState) -> None:
    cpu, mem = machineReset.cpu, machineReset.memory
    cpu.program_counter = 0xBCE2
    cpu.reg_a = 0b10000001
    mem[0xBCE2] = 0x0A  # ASL
    mem[0xBCE3] = 0x4A  # LSR
    cpu.fetch_decode_execute(machineReset)
    assert cpu.reg_a == 0b00000010 and cpu.flag_c
    cpu.fetch_decode_execute(machineReset)
    assert cpu.reg_a == 0b00000001 and not cpu.flag_c


def test_cpu_ins_rol_ror_acc(machineReset: MachineState) -> None:
    cpu, mem = machineReset.cpu, machineReset.memory
    cpu.program_counter = 0xBCE2
    cpu.reg_a = 0b10000001
    cpu.flag_c = True
    mem[0xBCE2] = 0x2A  # ROL
    mem[0xBCE3] = 0x6A  # ROR
    cpu.fetch_decode_execute(machineReset)
    assert cpu.reg_a == 0b00000011 and cpu.flag_c  # Bit 7 goes to carry, carry goes to bit 0
    cpu.fetch_decode_execute(machineReset)
    assert cpu.reg_a == 0b10000001 and cpu.flag_c  # Rotates back


# ==========================================
# JUMPS AND CALLS
# ==========================================

def test_cpu_ins_jmp_abs(machineReset: MachineState) -> None:
    cpu, mem = machineReset.cpu, machineReset.memory
    cpu.program_counter = 0xBCE2
    mem[0xBCE2] = 0x4C  # JMP Abs
    mem[0xBCE3] = 0xAD  # Low
    mem[0xBCE4] = 0xDE  # High (Target: 0xDEAD)
    cpu.fetch_decode_execute(machineReset)
    assert cpu.program_counter == 0xDEAD


def test_cpu_ins_jsr_rts(machineReset: MachineState) -> None:
    cpu, mem = machineReset.cpu, machineReset.memory
    cpu.program_counter = 0xBCE2
    mem[0xBCE2] = 0x20  # JSR Abs
    mem[0xBCE3] = 0x00  # Low
    mem[0xBCE4] = 0x05  # High (Target 0x0500)
    mem[0x0500] = 0x60  # RTS
    cpu.fetch_decode_execute(machineReset)  # Run JSR
    assert cpu.program_counter == 0x0500
    assert mem[0x01FF] == 0xBC and mem[0x01FE] == 0xE4  # Pushed PC+2
    cpu.fetch_decode_execute(machineReset)  # Run RTS
    assert cpu.program_counter == 0xBCE5  # Returns to instruction after JSR


# ==========================================
# BRANCHES
# ==========================================

def test_cpu_ins_branches(machineReset: MachineState) -> None:
    cpu, mem = machineReset.cpu, machineReset.memory
    # Using BEQ (Branch if Equal / Zero set) as representative for relative branching logic
    cpu.program_counter = 0xBCE2
    cpu.flag_z = True
    mem[0xBCE2] = 0xF0  # BEQ
    mem[0xBCE3] = 0x05  # Jump forward 5 bytes
    cpu.fetch_decode_execute(machineReset)
    assert cpu.program_counter == 0xBCE9  # BCE2 + 2 (instr length) + 5 = BCE9

    cpu.program_counter = 0xBCE2
    cpu.flag_z = False
    mem[0xBCE2] = 0xF0  # BEQ
    mem[0xBCE3] = 0x05
    cpu.fetch_decode_execute(machineReset)
    assert cpu.program_counter == 0xBCE4  # Did not branch


# ==========================================
# FLAGS & SYSTEM
# ==========================================

def test_cpu_ins_flags(machineReset: MachineState) -> None:
    cpu, mem = machineReset.cpu, machineReset.memory
    cpu.program_counter = 0xBCE2
    mem[0xBCE2] = 0x38  # SEC
    mem[0xBCE3] = 0xF8  # SED
    mem[0xBCE4] = 0x78  # SEI
    mem[0xBCE5] = 0x18  # CLC
    mem[0xBCE6] = 0xD8  # CLD
    mem[0xBCE7] = 0x58  # CLI
    mem[0xBCE8] = 0xB8  # CLV

    # Test Sets
    cpu.fetch_decode_execute(machineReset)
    cpu.fetch_decode_execute(machineReset)
    cpu.fetch_decode_execute(machineReset)
    assert cpu.flag_c and cpu.flag_d and cpu.flag_i

    # Test Clears
    cpu.flag_v = True
    cpu.fetch_decode_execute(machineReset)
    cpu.fetch_decode_execute(machineReset)
    cpu.fetch_decode_execute(machineReset)
    cpu.fetch_decode_execute(machineReset)
    assert not cpu.flag_c and not cpu.flag_d and not cpu.flag_i and not cpu.flag_v


def test_cpu_ins_nop(machineReset: MachineState) -> None:
    cpu, mem = machineReset.cpu, machineReset.memory
    cpu.program_counter = 0xBCE2
    mem[0xBCE2] = 0xEA  # NOP
    cpu.fetch_decode_execute(machineReset)
    assert cpu.program_counter == 0xBCE3


def test_cpu_ins_brk(machineReset: MachineState) -> None:
    cpu, mem = machineReset.cpu, machineReset.memory
    cpu.program_counter = 0xBCE2
    mem[0xBCE2] = 0x00  # BRK
    with pytest.raises(StopIteration):
        cpu.fetch_decode_execute(machineReset)
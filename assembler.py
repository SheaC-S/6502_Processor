from lib2to3.pygram import Symbols

from instructions import instruction_table, AddressMode


class Assembler:
    def __init__(assembler : 'Assembler') -> None:
        assembler.opcodes = {}

        for opcode_hex, instruction in instruction_table.items():
            key = (instruction.name, instruction.mode)
            assembler.opcodes[key] = opcode_hex

            # print(assembler.opcodes)

    def compile(assembler : 'Assembler', source_code : str) -> tuple[list[int], dict[int,int]]:
        machine_code : list[int] = []
        source_map : dict[int, int] = {}
        symbol_table : dict[str, int] = {}
        lines = source_code.strip().split('\n')

        for line_num, line in enumerate(lines, start = 1):
            original_line = line.strip()
            line = line.split(';')[0].strip()
            if not line:
                continue

            source_map[len(machine_code)] = line_num
            parts = line.upper().split()

            match parts:

                case [mnemonic]:
                    # Implied
                    opcode = assembler.opcodes.get((mnemonic, AddressMode.IMPLIED))
                    if opcode is None:
                        raise SyntaxError(f"Line {line_num}: Unknown instruction")
                    machine_code.append(opcode)

                case [mnemonic, "A" | "a"]:
                    # Accumulator
                    opcode = assembler.opcodes.get((mnemonic, AddressMode.ACCUMULATOR))
                    if opcode is None:
                        raise SyntaxError(f"Line {line_num}: Unknown instruction '{mnemonic} A'")
                    machine_code.append(opcode)

                case [mnemonic, operand] if operand.startswith('#$'):
                    # Immediate
                    opcode = assembler.opcodes.get((mnemonic, AddressMode.IMMEDIATE))
                    if opcode is None:
                        raise SyntaxError(f"Line {line_num}: Unknown instruction")

                    try:
                        value = int(operand[2:], 16)
                    except ValueError:
                        raise SyntaxError(f"Line {line_num}: Invalid hex value")

                    if value > 0xFF:
                        raise SyntaxError(f"Line {line_num}: Value too large - must be 8-bit")

                    machine_code.append(opcode)
                    machine_code.append(value)

                case [mnemonic, operand] if operand.startswith('$'):
                    # Checking to ensure no values are higher than 16 bit
                    try:
                        address = int(operand[1:], 16)
                    except ValueError:
                        raise SyntaxError(f"Line {line_num}: Invalid hex value")

                    # Relative
                    opcode = assembler.opcodes.get((mnemonic, AddressMode.RELATIVE))
                    if opcode is not None:
                        if address > 0xFF:
                            raise SyntaxError(f"Line {line_num}: Relative offset must be 8-bit")
                        machine_code.append(opcode)
                        machine_code.append(address)
                        continue

                    # Zero page
                    if address <= 0xFF:
                        opcode = assembler.opcodes.get((mnemonic, AddressMode.ZERO_PAGE))
                        if opcode is not None:
                            machine_code.append(opcode)
                            machine_code.append(address)
                            continue

                    # Absolute
                    opcode = assembler.opcodes.get((mnemonic, AddressMode.ABSOLUTE))
                    if opcode is None:
                        raise SyntaxError(f"Line {line_num}: Instruction doesn't support this memory addressing mode")

                    low_byte = address & 0xFF
                    high_byte = (address >> 8) & 0xFF

                    machine_code.append(opcode)
                    machine_code.append(low_byte)
                    machine_code.append(high_byte)

                case _:
                    raise SyntaxError(f"Line {line_num}: Unsupported address mode")

        return machine_code, source_map
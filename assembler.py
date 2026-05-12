from lib2to3.pygram import Symbols

from instructions import instruction_table, AddressMode


class Assembler:
    def __init__(assembler : 'Assembler') -> None:
        assembler.opcodes = {}

        for opcode_hex, instruction in instruction_table.items():
            key = (instruction.name, instruction.mode)
            assembler.opcodes[key] = opcode_hex

            # print(assembler.opcodes)

    def compile(assembler : 'Assembler', source_code : str, start_address : int) -> tuple[list[int], dict[int,int]]:
        machine_code : list[int] = []
        source_map : dict[int, int] = {}
        symbol_table : dict[str, int] = {}
        program_counter : int = start_address
        clean_lines : list[tuple] = []
        lines = source_code.strip().split('\n')

        for line_num, line in enumerate(lines, start = 0):
            original_line = line.strip()
            line = line.split(';')[0].strip()
            if not line:
                continue

            # For any constant values...
            if '=' in line:
                name_str, val_str = line.split('=', 1)
                const_name = name_str.strip().upper()
                const_val_str = val_str.strip().upper()

                try:
                    if const_val_str.startswith('$'):
                        const_val = int(const_val_str[1:], 16)
                    else:
                        const_val = int(const_val_str)
                    symbol_table[const_name] = const_val
                except ValueError:
                    raise SyntaxError(f"Line {line_num}: Invalid constant value '{const_val_str}'")

                continue

            parts = line.upper().split()

            # Collects all the labels (LOOP:)
            if parts[0].endswith(':'):
                label_name = parts[0][:-1]
                symbol_table[label_name] = program_counter
                parts.pop(0)

            if not parts:
                continue

            # Determine instruction size for the program counter
            mnemonic = parts[0]
            operand = parts[1] if len(parts) > 1 else None

            # Store a list of usable lines for the second part of compilation
            clean_lines.append((line_num, mnemonic, operand, program_counter))

            if operand is None or operand == 'A':
                program_counter += 1
            elif operand.startswith('#'):
                program_counter += 2
            elif operand.startswith('$'):
                address = int(operand[1:], 16)
                program_counter += 2 if address <= 0xFF else 3
            elif operand in symbol_table:
                target_value = symbol_table[operand]
                program_counter += 2 if target_value <= 0xFF else 3
            else:
                if assembler.opcodes.get((mnemonic, AddressMode.RELATIVE)):
                    program_counter += 2
                else:
                    program_counter += 3

        for line_num, mnemonic, operand, instruction_pc in clean_lines:
            source_map[len(machine_code)] = line_num

            # Resolve labels and constants into hex values
            if operand is not None and not operand.startswith(('#$', '$', 'A')):
                is_immediate = operand.startswith('#')
                symbol_name = operand[1:] if is_immediate else operand

                if symbol_name not in symbol_table:
                    raise SyntaxError(f"Line {line_num}: Unknown label/constant '{symbol_name}'")

                target_value = symbol_table[symbol_name]

                if is_immediate:
                    # Constant being used as an immediate value (e.g., LDA)
                    if target_value > 0xFF:
                        raise SyntaxError(f"Line {line_num}: Immediate value '{symbol_name}' too large - must be 8-bit")
                    operand = f"#${target_value:02X}"
                else:
                    # Constant or label being used as an address
                    if assembler.opcodes.get((mnemonic, AddressMode.RELATIVE)):
                        offset = target_value - (instruction_pc + 2)
                        if offset < -128 or offset > 127:
                            raise SyntaxError(f"Line {line_num}: Branch target '{symbol_name}' is out of range")
                        operand = f"${offset & 0xFF:02X}"
                    else:
                        operand = f"${target_value:04X}"

            parts = [mnemonic]
            if operand is not None:
                parts.append(operand)

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
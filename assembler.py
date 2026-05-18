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

            clean_operand = operand

            if clean_operand is not None:
                if clean_operand.endswith(',X') or clean_operand.endswith(',Y'):
                    clean_operand = clean_operand[:-2]  # Strips the modifier off

            clean_lines.append((line_num, mnemonic, operand, program_counter))

            if clean_operand is None or clean_operand == 'A':
                program_counter += 1
            elif clean_operand.startswith('#'):
                program_counter += 2
            elif clean_operand.startswith('$'):
                address = int(clean_operand[1:], 16)
                program_counter += 2 if address <= 0xFF else 3
            elif clean_operand.startswith('('):
                if clean_operand.endswith(',X)') or clean_operand.endswith('),Y'):
                    program_counter += 2
                else:
                    program_counter += 3
            elif clean_operand in symbol_table:
                target_value = symbol_table[clean_operand]
                program_counter += 2 if target_value <= 0xFF else 3
            else:
                if assembler.opcodes.get((mnemonic, AddressMode.RELATIVE)):
                    program_counter += 2
                else:
                    program_counter += 3

        for line_num, mnemonic, operand, instruction_pc in clean_lines:
            source_map[len(machine_code)] = line_num

            mode_override = None
            indexed_x = False
            indexed_y = False

            # 2. MUST WRAP ALL STRING CHECKS IN THIS IF STATEMENT:
            if operand is not None:

                # Indirect addressing checks
                if operand.startswith('('):
                    if operand.endswith(",X)"):
                        mode_override = AddressMode.INDIRECT_X
                        operand = operand.replace("(", "").replace(",X)", "")
                    elif operand.endswith("),Y"):
                        mode_override = AddressMode.INDIRECT_Y
                        operand = operand.replace("(", "").replace("),Y", "")
                    elif operand.endswith(")"):
                        mode_override = AddressMode.INDIRECT
                        operand = operand.replace("(", "").replace(")", "")

                # Indexed addressing checks
                elif operand.endswith(",X"):
                    indexed_x = True
                    operand = operand.replace(",X", "")
                elif operand.endswith(",Y"):
                    indexed_y = True
                    operand = operand.replace(",Y", "")

            if operand is not None and not operand.startswith(('#$', '$', 'A')):
                is_immediate = operand.startswith('#')

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

                case [mnemonic, operand] if mode_override is not None:
                    opcode = assembler.opcodes.get((mnemonic, mode_override))
                    if opcode is None:
                        raise SyntaxError(f"Line {line_num}: Instruction doesn't support indirect addressing")

                    try:
                        # operand is now just the hex string (e.g., "$10" or "$0300")
                        if operand.startswith('$'):
                            address = int(operand[1:], 16)
                        else:
                            address = int(operand)
                    except ValueError:
                        raise SyntaxError(f"Line {line_num}: Invalid hex value")

                    machine_code.append(opcode)

                    if mode_override in [AddressMode.INDIRECT_X, AddressMode.INDIRECT_Y]:
                        if address > 0xFF:
                            raise SyntaxError(f"Line {line_num}: Indirect X/Y requires an 8-bit Zero Page address")
                        machine_code.append(address & 0xFF)

                    elif mode_override == AddressMode.INDIRECT:
                        machine_code.append(address & 0xFF)
                        machine_code.append((address >> 8) & 0xFF)

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
                    try:
                        address = int(operand[1:], 16)
                    except ValueError:
                        raise SyntaxError(f"Line {line_num}: Invalid hex value")

                    # Relative Branching
                    opcode = assembler.opcodes.get((mnemonic, AddressMode.RELATIVE))
                    if opcode is not None:
                        if address > 0xFF:
                            raise SyntaxError(f"Line {line_num}: Relative offset must be 8-bit")
                        machine_code.append(opcode)
                        machine_code.append(address)
                        continue

                    # Zero Page
                    elif address <= 0xFF:
                        if indexed_x:
                            target_mode = AddressMode.ZERO_PAGE_X
                        elif indexed_y:
                            target_mode = AddressMode.ZERO_PAGE_Y
                        else:
                            target_mode = AddressMode.ZERO_PAGE

                        opcode = assembler.opcodes.get((mnemonic, target_mode))
                        if opcode is not None:
                            machine_code.append(opcode)
                            machine_code.append(address)
                            continue

                    # 3. Check Absolute
                    if indexed_x:
                        target_mode = AddressMode.ABSOLUTE_X
                    elif indexed_y:
                        target_mode = AddressMode.ABSOLUTE_Y
                    else:
                        target_mode = AddressMode.ABSOLUTE

                    opcode = assembler.opcodes.get((mnemonic, target_mode))
                    if opcode is None:
                        raise SyntaxError(f"Line {line_num}: Instruction doesn't support this memory addressing mode")

                    machine_code.append(opcode)
                    machine_code.append(address & 0xFF)
                    machine_code.append((address >> 8) & 0xFF)

                case[mnemonic, operand] if mode_override is not None:
                    opcode = assembler.opcodes.get((mnemonic, mode_override))
                    if opcode is None:
                        raise SyntaxError(f"Line {line_num}: Instruction doesn't support indirect addressing")

                    try:
                        # The operand was cleaned above, so it's just the hex string (e.g., "$10" or "$2000")
                        if operand.startswith('$'):
                            address = int(operand[1:], 16)
                        else:
                            address = int(operand)  # Fallback if it was a label resolved to an int
                    except ValueError:
                        raise SyntaxError(f"Line {line_num}: Invalid hex value")

                    machine_code.append(opcode)

                    # INDIRECT_X and INDIRECT_Y only take a 1-byte Zero Page address
                    if mode_override in [AddressMode.INDIRECT_X, AddressMode.INDIRECT_Y]:
                        if address > 0xFF:
                            raise SyntaxError(f"Line {line_num}: Indirect X/Y requires an 8-bit Zero Page address")
                        machine_code.append(address & 0xFF)

                    # Absolute INDIRECT (JMP) takes a 2-byte address
                    elif mode_override == AddressMode.INDIRECT:
                        machine_code.append(address & 0xFF)
                        machine_code.append((address >> 8) & 0xFF)

                case _:
                    raise SyntaxError(f"Line {line_num}: Unsupported address mode")

        return machine_code, source_map
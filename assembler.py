from lib2to3.pygram import Symbols

from instructions import instruction_table, AddressMode


class Assembler:
    def __init__(assembler : 'Assembler') -> None:
        assembler.opcodes = {}

        for opcode_hex, instruction in instruction_table.items():
            key = (instruction.name, instruction.mode)
            assembler.opcodes[key] = opcode_hex



    def compile(assembler : 'Assembler', source_code : str) -> list[int]:
        machine_code : list[int] = []
        lines = source_code.strip().split('\n')

        for line_num, line in enumerate(lines, start = 1):
            original_line = line.strip()
            line = line.strip(';')[0].strip()
            if not line:
                continue

            parts = line.upper().split()
            mnemonic = parts[0]

            if len(parts) == 1:
                opcode = assembler.opcodes.get((mnemonic, AddressMode.IMPLIED))
                if opcode is None:
                    raise SyntaxError(f"Line {line_num}: Unknown instruction")
                machine_code.append(opcode)

            else:
                operand = parts[1]

                if operand.startswith('#$'):
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

                elif operand.startswith('$') and len(operand) == 5:
                    ## Absolute
                    opcode = assembler.opcodes.get((mnemonic, AddressMode.ABSOLUTE))
                    if opcode is None:
                        raise SyntaxError(f"Line {line_num}: Doesn't support absolute addressing")

                    try:
                        address = int(operand[1:], 16)
                    except ValueError:
                        raise SyntaxError(f"Line {line_num}: Invalid hex value")

                    low_byte = address & 0xFF
                    high_byte = (address >> 8) & 0xFF

                    machine_code.append(opcode)
                    machine_code.append(low_byte)
                    machine_code.append(high_byte)

                else:
                    raise SyntaxError(f"Line {line_num}: Unsupported address mode")

        return machine_code
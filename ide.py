import copy

from PyQt6.QtCore import QTimer, QSize, Qt, QRegularExpression
from PyQt6.QtGui import QFont, QPalette, QSyntaxHighlighter, QTextCharFormat, QColor, QIcon, QFontDatabase
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPlainTextEdit, QPushButton, \
    QApplication, QGroupBox, QLabel, QSlider, QComboBox

from exception import safe_execution
from memory import Memory
from processor import Processor
from screen import Screen
from state import MachineState
from instructions import instruction_table
from assembler import Assembler

import sys
import PyQt6

class IDE(QMainWindow):
    def __init__(ide : "IDE", processor : Processor, memory : Memory) -> None:
        super().__init__()
        ide.processor = processor
        ide.memory = memory
        ide.state = MachineState(ide.processor, ide.memory)
        ide.assembler = Assembler()
        ide.is_running = False
        ide.state_stack = []

        ide.setWindowTitle("6502 Virtual Console")
        ide.resize(900,900)
        ide.setWindowIcon(QIcon('cpu_image.webp'))

        # Overall layout
        central_widget = QWidget()
        ide.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Layout for editor
        editor_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        ide.editor = CodeEditor()
        ide.editor.setPlaceholderText("Write your code here!")
        ide.load_button = QPushButton("Load")
        ide.run_button = QPushButton("Run")
        ide.step_forward_button = QPushButton("Step forward")
        ide.step_back_button = QPushButton("Step back")
        ide.toggle_registers_button = QPushButton("Toggle Registers")
        ide.toggle_memory_button = QPushButton("Toggle Memory Panel")

        # Speed control
        ide.speed_label = QLabel("Speed:")
        ide.speed_slider = QSlider(Qt.Orientation.Horizontal)
        ide.speed_slider.setRange(1, 1000)  # 1 to 1000 instructions per frame
        ide.speed_slider.setValue(1)  # Default to slow mode
        ide.speed_slider.setMinimumWidth(100)

        ide.load_button.clicked.connect(ide.load_code)
        ide.run_button.clicked.connect(ide.toggle_execution)
        ide.step_forward_button.clicked.connect(ide.step_forward)
        ide.step_back_button.clicked.connect(ide.step_backward)
        ide.toggle_registers_button.clicked.connect(ide.toggle_registers)
        ide.toggle_memory_button.clicked.connect(ide.toggle_memory_map)

        editor_layout.addWidget(ide.editor)
        button_layout.addWidget(ide.load_button)
        button_layout.addWidget(ide.run_button)
        button_layout.addWidget(ide.step_forward_button)
        button_layout.addWidget(ide.step_back_button)
        button_layout.addWidget(ide.toggle_registers_button)
        button_layout.addWidget(ide.toggle_memory_button)
        button_layout.addWidget(ide.speed_label)
        button_layout.addWidget(ide.speed_slider)
        editor_layout.addLayout(button_layout)

        # New Output Console
        ide.console_output = QPlainTextEdit()
        ide.console_output.setReadOnly(True)
        ide.console_output.setMaximumHeight(150)
        ide.console_output.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: Courier;")

        # Layout for emulated screen
        ide.vscreen = Screen(ide.memory)

        # Layout for CPU stats
        ide.register_panel = QGroupBox("CPU Registers")
        register_layout = QVBoxLayout()
        ide.register_panel.setLayout(register_layout)

        ide.register_panel.setStyleSheet("""
                QLabel {
                    font-family: Verdana;
                    font-size: 16px;
                    }
                """)

        ide.label_program_counter = QLabel("Program Counter: $0000")
        ide.label_stack_pointer = QLabel("Stack Pointer: $00")
        ide.label_accumulator = QLabel("Accumulator: $00")
        ide.label_x_reg = QLabel("X Register: $00")
        ide.label_y_reg = QLabel("Y Register: $00\n")

        ide.label_carry_flag = QLabel("Carry Flag: 0")
        ide.label_zero_flag = QLabel("Zero Flag: 0")
        ide.label_interrupt_flag = QLabel("Interrupt Flag: 0")
        ide.label_decimal_flag = QLabel("Decimal Flag: 0")
        ide.label_break_flag = QLabel("Break Flag: 0")
        ide.label_overflow_flag = QLabel("Overflow Flag: 0")
        ide.label_negative_flag = QLabel("Negative Flag: 0")

        register_layout.addWidget(ide.label_program_counter)
        register_layout.addWidget(ide.label_stack_pointer)
        register_layout.addWidget(ide.label_accumulator)
        register_layout.addWidget(ide.label_x_reg)
        register_layout.addWidget(ide.label_y_reg)

        register_layout.addWidget(ide.label_carry_flag)
        register_layout.addWidget(ide.label_zero_flag)
        register_layout.addWidget(ide.label_interrupt_flag)
        register_layout.addWidget(ide.label_decimal_flag)
        register_layout.addWidget(ide.label_break_flag)
        register_layout.addWidget(ide.label_overflow_flag)
        register_layout.addWidget(ide.label_negative_flag)

        ide.register_panel.setVisible(False)

        ####################################
        # Memory viewer
        ide.memory_panel = QGroupBox("Memory Panel")
        memory_layout = QVBoxLayout()

        ide.memory_page_selector = QComboBox()
        ide.memory_page_selector.addItems([
            "$00 - Zero Page",
            "$01 - Stack",
            "$02 - General Memory",
            "$C0 - Virtual Screen"
        ])

        ide.page_map = [0x00, 0x01, 0x02, 0xC0]
        ide.memory_display = QPlainTextEdit()
        ide.memory_display.setReadOnly(True)
        ide.memory_display.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        ide.memory_display.setMinimumWidth(550)
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(10)
        ide.memory_display.setFont(font)

        memory_layout.addWidget(QLabel("Live Memory Viewer"))
        memory_layout.addWidget(ide.memory_page_selector)
        memory_layout.addWidget(ide.memory_display)
        ide.memory_panel.setLayout(memory_layout)
        ide.memory_panel.setVisible(False)

        ide.memory_page_selector.currentIndexChanged.connect(ide.update_memory_display)

        ########################

        # Main layout
        main_layout.addLayout(editor_layout)
        right_layout = QVBoxLayout()
        sub_layout = QHBoxLayout()
        right_layout.addWidget(ide.vscreen)
        right_layout.addWidget(ide.console_output)

        sub_layout.addWidget(ide.register_panel)
        sub_layout.addWidget(ide.memory_panel)
        right_layout.addLayout(sub_layout)

        main_layout.addLayout(right_layout)

        ide.timer = QTimer()
        ide.timer.timeout.connect(ide.emulator_tick)
        ide.log_to_console("Welcome to the 6502 console emulator!")

    def toggle_registers(ide : 'ide') -> None:
        is_visible = ide.register_panel.isVisible()
        ide.register_panel.setVisible(not is_visible)

        if not is_visible:
            ide.update_register_display()

    def toggle_memory_map(ide : 'ide') -> None:
        is_visible = ide.memory_panel.isVisible()
        ide.memory_panel.setVisible(not is_visible)

        if not is_visible:
            ide.update_register_display()

    def update_register_display(ide : 'ide') -> None:
        processor = ide.processor

        # print("Hello world!")

        ide.label_program_counter.setText(f"Program Counter: ${processor.program_counter:04X}")
        ide.label_stack_pointer.setText(f"Stack Pointer: ${processor.stack_pointer:02X}")
        ide.label_accumulator.setText(f"Accumulator: ${processor.reg_a:02X}")
        ide.label_x_reg.setText(f"X Register: ${processor.reg_x:02X}")
        ide.label_y_reg.setText(f"Y Register: ${processor.reg_y:02X}\n")

        ide.label_carry_flag.setText(f"Carry Flag: {int(processor.flag_c)}")
        ide.label_zero_flag.setText(f"Zero Flag: {int(processor.flag_z)}")
        ide.label_interrupt_flag.setText(f"Interrupt Flag: {int(processor.flag_i)}")
        ide.label_decimal_flag.setText(f"Decimal Flag: {int(processor.flag_d)}")
        ide.label_break_flag.setText(f"Break Flag: {int(processor.flag_b)}")
        ide.label_overflow_flag.setText(f"Overflow Flag: {int(processor.flag_v)}")
        ide.label_negative_flag.setText(f"Negative Flag: {int(processor.flag_n)}")

    def log_to_console(ide: 'IDE', message: str) -> None:
        ide.console_output.appendPlainText(message)

    def save_state_snapshot(ide : 'ide') -> None:
        if len(ide.state_stack) > 500:
            ide.state_stack.pop(0)

        saved_state = copy.deepcopy(ide.state)
        ide.state_stack.append(saved_state)

    def update_editor_highlight(ide : 'ide') -> None:
        program_counter = ide.processor.program_counter

        if hasattr(ide, "address_to_line") and program_counter in ide.address_to_line:
            line_to_highlight = ide.address_to_line[program_counter]
            ide.editor.set_active_line(line_to_highlight)
        else:
            ide.editor.clear_active_line()

    def update_memory_display(ide : 'ide') -> None:
        combo_index = ide.memory_page_selector.currentIndex()
        page_number = ide.page_map[combo_index]

        start_address = page_number * 256
        lines = []
        lines.append("Addr  | 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F")
        lines.append("-" * 55)

        for row in range(16):
            row_address = start_address + (row * 16)
            hex_bytes = []

            for col in range(16):
                val = ide.state.memory.memory[row_address + col]
                hex_bytes.append(f"{val:02X}")

            hex_string = " ".join(hex_bytes)
            lines.append(f"${row_address:04X} | {hex_string}")

        ide.memory_display.setPlainText("\n".join(lines))

    @safe_execution
    def load_code(ide : 'ide') -> None:
        if ide.is_running:
            ide.is_running = False
            ide.timer.stop()
            ide.run_button.setText("Run")
            ide.log_to_console("Execution stopped")
        else:
            source_code = ide.editor.toPlainText()
            if not source_code.strip():
                ide.log_to_console("ERROR: No code to run!")
                return

            vmem_start = ide.vscreen.vmem_start
            vmem_size = ide.vscreen.width * ide.vscreen.height
            ide.memory.memory[vmem_start: vmem_start + vmem_size] = [0b00000000] * vmem_size
            ide.processor.reset()

            machine_code, source_map = ide.assembler.compile(source_code, ide.processor.program_counter)
            start_address = ide.processor.program_counter

            ide.address_to_line = {
                (start_address + offset): line_num
                for offset, line_num in source_map.items()
            }

            for i, byte in enumerate(machine_code):
                ide.memory[start_address + i] = byte

            ide.log_to_console(f"Success! Loaded {len(machine_code)} bytes into memory.")

            if ide.register_panel.isVisible():
                ide.update_register_display()

            if ide.memory_panel.isVisible():
                ide.update_memory_display()

            if ide.state.memory.screen_refresh:
                ide.vscreen.render()
                ide.state.memory.screen_refresh = False

            ide.update_editor_highlight()

    @safe_execution
    def toggle_execution(ide : 'ide') -> None:

        if ide.is_running:
            ide.is_running = False
            ide.timer.stop()
            ide.editor.clear_active_line()
            ide.run_button.setText("Run")
            ide.log_to_console("Execution stopped")
        else:
            # print("Running...")
            ide.is_running = True
            ide.run_button.setText("Stop")
            ide.timer.start(16)

    @safe_execution
    def step_forward(ide : 'ide') -> None:

        if ide.is_running:
            ide.log_to_console("Pause the execution first!")
            return

        ide.save_state_snapshot()

        ide.processor.fetch_decode_execute(ide.state)
        ide.update_register_display()

        ide.update_editor_highlight()

        if ide.register_panel.isVisible():
            ide.update_register_display()

        if ide.state.memory.screen_refresh:
            ide.vscreen.render()
            ide.state.memory.screen_refresh = False

    def step_backward(ide : 'ide') -> None:

        if ide.is_running:
            ide.log_to_console("Pause the execution first!")
            return

        if not ide.state_stack:
            ide.log_to_console("No previous state to step back to!")
            return

        old_state = ide.state_stack.pop()

        ide.state = old_state
        ide.processor = old_state.cpu
        ide.memory = old_state.memory
        ide.vscreen.memory = old_state.memory

        ide.update_editor_highlight()

        if ide.register_panel.isVisible():
            ide.update_register_display()

        if ide.state.memory.screen_refresh:
            ide.vscreen.render()
            ide.state.memory.screen_refresh = False

        ide.log_to_console(f"Step back to: {len(ide.state_stack)}")

    @safe_execution
    def emulator_tick(ide : 'ide') -> None:
        batch_size = ide.speed_slider.value()

        for _ in range(batch_size):
            ide.processor.fetch_decode_execute(ide.state)

        if ide.register_panel.isVisible():
            ide.update_register_display()

        if ide.memory_panel.isVisible():
            ide.update_memory_display()

        if ide.state.memory.screen_refresh:
            ide.vscreen.render()
            ide.state.memory.screen_refresh = False

        if batch_size < 5:
            ide.update_editor_highlight()
        else:
            ide.editor.clear_active_line()

        """
        except StopIteration:
            ide.is_running = False
            ide.timer.stop()
            ide.run_button.setText("Run")
            ide.log_to_console("Program finished (Hit BRK / $00).")
            ide.editor.clear_active_line()

        except Exception as e:
            ide.is_running = False
            ide.timer.stop()
            ide.run_button.setText("Run")

            import traceback
            error_message = traceback.format_exc()
            ide.log_to_console(f"ERROR:\n {error_message}")
        """



class CodeEditor(PyQt6.QtWidgets.QPlainTextEdit):

    def __init__(editor : 'CodeEditor') -> None:
        super().__init__()

        editor.setFont(PyQt6.QtGui.QFont("Courier", 12))
        editor.lineNumberArea = LineNumberArea(editor)
        editor.blockCountChanged.connect(editor.updateLineNumberAreaWidth)
        editor.updateRequest.connect(editor.updateLineNumberArea)

        editor.updateLineNumberAreaWidth(0)

        editor.highlighter = AssemblyHighlighter(editor.document())

    def lineNumberAreaWidth(editor : 'CodeEditor') -> int:
        digits = len(str(editor.blockCount()))
        space = editor.fontMetrics().horizontalAdvance('9') * digits
        em = editor.fontMetrics().horizontalAdvance('M')
        padding = int(em * 1.5)

        return space + padding

    def updateLineNumberAreaWidth(editor : 'CodeEditor', _) -> None:
        editor.setViewportMargins(editor.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(editor : 'CodeEditor', rect, dy) -> None:
        if dy:
            editor.lineNumberArea.scroll(0, dy)
        else:
            editor.lineNumberArea.update(0, rect.y(), editor.lineNumberArea.width(), rect.height())
        if rect.contains(editor.viewport().rect()):
            editor.updateLineNumberAreaWidth(0)

    def resizeEvent(editor : 'CodeEditor', event) -> None:
        super().resizeEvent(event)
        cr = editor.contentsRect()
        corrected_width = editor.lineNumberAreaWidth()

        editor.lineNumberArea.setGeometry(PyQt6.QtCore.QRect(cr.left(), cr.top(), corrected_width, cr.height()))

    def lineNumberAreaPaintEvent(editor : 'CodeEditor', event):
        painter = PyQt6.QtGui.QPainter(editor.lineNumberArea)
        painter.setFont(editor.font())

        painter.fillRect(event.rect(), editor.palette().base())

        block = editor.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(editor.blockBoundingGeometry(block).translated(editor.contentOffset()).top())
        bottom = top + int(editor.blockBoundingRect(block).height())

        pen = PyQt6.QtGui.QPen(editor.palette().text().color())
        color = pen.color()
        color.setAlpha(127)
        pen.setColor(color)
        painter.setPen(pen)

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                em = editor.fontMetrics().horizontalAdvance('M')
                total_padding = int(em * 1.5)
                left_padding = total_padding // 2
                right_padding = total_padding // 2

                rect = PyQt6.QtCore.QRect(int(left_padding), int(top), int(editor.lineNumberArea.width() - left_padding - right_padding), int(editor.fontMetrics().height()))

                painter.drawText(rect, PyQt6.QtCore.Qt.AlignmentFlag.AlignVCenter | PyQt6.QtCore.Qt.AlignmentFlag.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + int(editor.blockBoundingRect(block).height())
            blockNumber += 1

            splitter_pen = PyQt6.QtGui.QPen()
            splitter_pen.setColor(editor.palette().color(PyQt6.QtGui.QPalette.ColorRole.Accent))
            painter.setPen(splitter_pen)
            painter.drawLine(editor.lineNumberArea.width() - 1, event.rect().top(),
                             editor.lineNumberArea.width() - 1, event.rect().bottom())

    def set_active_line(editor: 'CodeEditor', line_number: int) -> None:
        selection = PyQt6.QtWidgets.QTextEdit.ExtraSelection()

        line_color = PyQt6.QtGui.QColor("#40FF0080")
        selection.format.setBackground(line_color)
        selection.format.setProperty(PyQt6.QtGui.QTextFormat.Property.FullWidthSelection, True)

        cursor = editor.textCursor()
        cursor.setPosition(editor.document().findBlockByNumber(line_number).position())
        selection.cursor = cursor

        editor.setExtraSelections([selection])

    def clear_active_line(editor: 'CodeEditor') -> None:
        editor.setExtraSelections([])

class LineNumberArea(PyQt6.QtWidgets.QWidget):

    def __init__(lines : 'LineNumberArea' ,editor) -> None:
        super().__init__(editor)
        lines.editor = editor

    def sizeHint(lines : 'LineNumberArea') -> QSize:
        return PyQt6.QtCore.QSize(lines.editor.lineNumberAreaWidth(), 0)

    def paintEvent(lines : 'LineNumberArea', event) -> None:
        lines.editor.lineNumberAreaPaintEvent(event)

class AssemblyHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlightingRules = []

        mnemonic_format = QTextCharFormat()
        mnemonic_format.setForeground(QColor("orange"))

        commands = list(set(instr.name for instr in instruction_table.values()))

        pattern = r"\b(?:" + "|".join(commands) + r")\b"
        regex = QRegularExpression(pattern, QRegularExpression.PatternOption.CaseInsensitiveOption)
        self.highlightingRules.append((regex, mnemonic_format))

        # Format for Hex Addresses (e.g., $8000, #$FF)
        hex_format = QTextCharFormat()
        hex_format.setForeground(QColor("#2d7ed2"))
        self.highlightingRules.append((QRegularExpression(r"#?\$[0-9A-Fa-f]+"), hex_format))

        # Format for Comments (e.g., ; This is a comment)
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("gray"))
        self.highlightingRules.append((QRegularExpression(r";.*"), comment_format))

        # Format for labels (e.g., LOOP:, SUB:)
        label_format = QTextCharFormat()
        label_format.setForeground(QColor("cyan"))
        self.highlightingRules.append((QRegularExpression(r'\b[A-Za-z_][A-Za-z0-9_]*:'), label_format))

    def highlightBlock(self, text: str) -> None:
        for pattern, format in self.highlightingRules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

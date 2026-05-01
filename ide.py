import traceback
from pickle import EXT2
from turtledemo.sorting_animate import Block

from PyQt6.QtCore import QTimer, QSize, Qt, QRegularExpression
from PyQt6.QtGui import QFont, QPalette, QSyntaxHighlighter, QTextCharFormat, QColor, QIcon
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPlainTextEdit, QPushButton, QApplication, QGroupBox, QLabel

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

        ide.load_button.clicked.connect(ide.load_code)
        ide.run_button.clicked.connect(ide.toggle_execution)
        ide.step_forward_button.clicked.connect(ide.step_forward)
        ide.step_back_button.clicked.connect(ide.step_backward)

        ide.toggle_registers_button.clicked.connect(ide.toggle_registers)
        editor_layout.addWidget(ide.editor)
        button_layout.addWidget(ide.load_button)
        button_layout.addWidget(ide.run_button)
        button_layout.addWidget(ide.step_forward_button)
        button_layout.addWidget(ide.step_back_button)
        button_layout.addWidget(ide.toggle_registers_button)
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
        ide.label_b_reg = QLabel("B Register: $00\n")

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
        register_layout.addWidget(ide.label_b_reg)

        register_layout.addWidget(ide.label_carry_flag)
        register_layout.addWidget(ide.label_zero_flag)
        register_layout.addWidget(ide.label_interrupt_flag)
        register_layout.addWidget(ide.label_decimal_flag)
        register_layout.addWidget(ide.label_break_flag)
        register_layout.addWidget(ide.label_overflow_flag)
        register_layout.addWidget(ide.label_negative_flag)

        ide.register_panel.setVisible(False)

        # Main layout
        main_layout.addLayout(editor_layout)
        right_layout = QVBoxLayout()
        right_layout.addWidget(ide.vscreen)
        right_layout.addWidget(ide.console_output)
        right_layout.addWidget(ide.register_panel)
        main_layout.addLayout(right_layout)

        ide.timer = QTimer()
        ide.timer.timeout.connect(ide.emulator_tick)

    def toggle_registers(ide : 'ide') -> None:
        is_visible = ide.register_panel.isVisible()
        ide.register_panel.setVisible(not is_visible)

        if not is_visible:
            ide.update_register_display()

    def update_register_display(ide : 'ide') -> None:
        processor = ide.processor

        print("Hello world!")

        ide.label_program_counter.setText(f"Program Counter: ${processor.program_counter:04X}")
        ide.label_stack_pointer.setText(f"SP: ${processor.stack_pointer:02X}")
        ide.label_accumulator.setText(f"Accumulator: ${processor.reg_a:02X}")
        ide.label_x_reg.setText(f"X Register: ${processor.reg_x:02X}")
        ide.label_b_reg.setText(f"B Register: ${processor.reg_b:02X}\n")

        ide.label_carry_flag.setText(f"Carry Flag: {int(processor.flag_c)}")
        ide.label_zero_flag.setText(f"Zero Flag: {int(processor.flag_z)}")
        ide.label_interrupt_flag.setText(f"Interrupt Flag: {int(processor.flag_i)}")
        ide.label_decimal_flag.setText(f"Decimal Flag: {int(processor.flag_d)}")
        ide.label_break_flag.setText(f"Break Flag: {int(processor.flag_b)}")
        ide.label_overflow_flag.setText(f"Overflow Flag: {int(processor.flag_v)}")
        ide.label_negative_flag.setText(f"Negative Flag: {int(processor.flag_n)}")

    def log_to_console(ide: 'IDE', message: str) -> None:
        ide.console_output.appendPlainText(message)

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

            try:
                vmem_start = ide.vscreen.vmem_start
                vmem_size = ide.vscreen.width * ide.vscreen.height
                ide.memory.memory[vmem_start: vmem_start + vmem_size] = [0b00000000] * vmem_size

                machine_code = ide.assembler.compile(source_code)

                start_address = 0xBCE2
                for i, byte in enumerate(machine_code):
                    ide.memory[start_address + i] = byte

                ide.log_to_console(f"Success! Loaded {len(machine_code)} bytes into memory.")

            except Exception as e:
                ide.is_running = False
                ide.log_to_console(f"ERROR: {str(e)}")

    def toggle_execution(ide : 'ide') -> None:

        if ide.is_running:
            ide.is_running = False
            ide.timer.stop()
            ide.run_button.setText("Run")
            ide.log_to_console("Execution stopped")
        else:
            print("Running...")

            try:
                ide.processor.reset()
                ide.is_running = True
                ide.run_button.setText("Stop")
                ide.timer.start(16)

            except Exception as e:
                ide.is_running = False
                ide.log_to_console(f"ERROR: {str(e)}")

    def step_forward(ide : 'ide') -> None:

        if ide.is_running:
            ide.log_to_console("Pause the execution first!")
            return

        try:
            ide.processor.fetch_decode_execute(ide.state)

            if ide.register_panel.isVisible():
                ide.update_register_display()

            ide.vscreen.render()

        except Exception as e:
            ide.log_to_console(f"ERROR: {str(e)}")

    def step_backward(ide : 'ide') -> None:
        if ide.is_running:
            ide.log_to_console("Pause the execution first!")
            return

        try:
            ide.processor.fetch_decode_execute(ide.state)

            if ide.register_panel.isVisible():
                ide.update_register_display()

            ide.vscreen.render()

        except Exception as e:
            ide.log_to_console(f"ERROR: {str(e)}")

    def emulator_tick(ide : 'ide') -> None:
        try:
            ide.processor.fetch_decode_execute(ide.state)

            if ide.register_panel.isVisible():
                ide.update_register_display()

            ide.vscreen.render()

        except Exception as e:
            ide.is_running = False
            ide.timer.stop()
            ide.run_button.setText("Run")

            import traceback
            error_message = traceback.format_exc()
            ide.log_to_console(f"ERROR:\n {error_message}")

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
        mnemonic_format.setForeground(QColor("pink"))

        commands = list(set(instr.name for instr in instruction_table.values()))

        pattern = r"\b(?:" + "|".join(commands) + r")\b"
        regex = QRegularExpression(pattern, QRegularExpression.PatternOption.CaseInsensitiveOption)
        self.highlightingRules.append((regex, mnemonic_format))

        # Format for Hex Addresses (e.g., $8000, #$FF)
        hex_format = QTextCharFormat()
        hex_format.setForeground(QColor("lightgreen"))
        self.highlightingRules.append((QRegularExpression(r"[$#][0-9A-Fa-f]+"), hex_format))

        # Format for Comments (e.g., ; This is a comment)
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("gray"))
        self.highlightingRules.append((QRegularExpression(r";.*"), comment_format))

    def highlightBlock(self, text: str) -> None:
        for pattern, format in self.highlightingRules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

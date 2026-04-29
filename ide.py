import traceback
from turtledemo.sorting_animate import Block

from PyQt6.QtCore import QTimer, QSize, Qt, QRegularExpression
from PyQt6.QtGui import QFont, QPalette, QSyntaxHighlighter, QTextCharFormat, QColor, QIcon
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QPushButton, QApplication

from memory import Memory
from processor import Processor
from screen import Screen
from state import MachineState
from instructions import instruction_table

import sys
import PyQt6

class IDE(QMainWindow):
    def __init__(ide : "IDE", processor : Processor, memory : Memory) -> None:
        super().__init__()
        ide.processor = processor
        ide.memory = memory
        ide.state = MachineState(ide.processor, ide.memory)
        ide.is_running = False
        ide.colour_phase = 0

        ide.setWindowTitle("6502 Virtual Console")
        ide.resize(900,600)
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
        ide.run_button = QPushButton("Run")
        ide.step_forward_button = QPushButton("Step forward")
        ide.step_back_button = QPushButton("Step back")
        ide.run_button.clicked.connect(ide.toggle_execution)
        editor_layout.addWidget(ide.editor)
        button_layout.addWidget(ide.run_button)
        button_layout.addWidget(ide.step_forward_button)
        button_layout.addWidget(ide.step_back_button)
        editor_layout.addLayout(button_layout)

        # Layout for emulated screen
        ide.vscreen = Screen(ide.memory)
        main_layout.addLayout(editor_layout)
        main_layout.addWidget(ide.vscreen)

        ide.timer = QTimer()
        ide.timer.timeout.connect(ide.emulator_tick)

    def toggle_execution(ide : 'ide') -> None:

        if ide.is_running:
            ide.is_running = False
            ide.timer.stop()
            ide.run_button.setText("Run")
        else:
            source_code = ide.editor.toPlainText()
            print("Running...")

            ide.processor.reset()
            ide.is_running = True
            ide.run_button.setText("Stop")
            ide.timer.start(16)

    def emulator_tick(ide : 'ide') -> None:
        try:
            '''for _ in range(1000):
                ide.processor.fetch_decode_execute(ide.state)'''

            '''
            ide.colour_phase = (ide.colour_phase + 1) % 256

            end_vram = ide.vscreen.vmem_start + 76800
            ide.memory.memory[ide.vscreen.vmem_start:end_vram] = [ide.colour_phase] * 76800
            '''

            ide.vscreen.render()

        except Exception as e:
            ide.is_running = False
            ide.timer.stop()
            ide.run_button.setText("Run")

            print("Crashed!")
            traceback.print_exc()

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

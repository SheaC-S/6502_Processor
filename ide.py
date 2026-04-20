import traceback

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QPushButton, QApplication

from memory import Memory
from processor import Processor
from screen import Screen
from state import MachineState

import sys
import PyQt6

class IDE(QMainWindow):
    def __init__(ide : "IDE", processor : Processor, memory : Memory) -> None:
        super().__init__()
        ide.processor = processor
        ide.memory = memory
        ide.state = MachineState(ide.processor, ide.memory)
        ide.is_running = False

        ide.setWindowTitle("6502 Virtual Console")
        ide.resize(900,600)

        # Overall layout
        central_widget = QWidget()
        ide.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Layout for editor
        editor_layout = QHBoxLayout()
        ide.editor = QPlainTextEdit()
        ide.editor.setFont(QFont("Courier", 12))
        ide.editor.setPlaceholderText("Write your code here!")
        ide.run_button = QPushButton("Run")
        ide.run_button.clicked.connect(ide.toggle_execution)
        editor_layout.addWidget(ide.editor)
        editor_layout.addWidget(ide.run_button)

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

            ide.cpu.reset()
            ide.is_running = True
            ide.run_button.setText("Stop")
            ide.timer.start(16)

    def emulator_tick(ide : 'ide') -> None:
        try:
            for _ in range(1000):
                ide.processor.fetch_decode_execute(ide.state)

            ide.vscreen.render()

        except Exception as e:
            ide.is_running = False
            ide.timer.stop()
            ide.run_button.setText("Run")

            print("\n" + "="*40)
            print("Crashed!")
            print("="*40)
            traceback.print_exc()

if __name__ == "__main__":
    proc = Processor()
    ram = Memory(size = 0x10000 * 2) # 64KB * 2
    state = MachineState(proc, ram)

    app = QApplication(sys.argv)
    window = IDE(proc, ram)
    window.show()

    sys.exit(app.exec())
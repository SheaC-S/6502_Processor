import sys

from PyQt6.QtWidgets import QApplication

from ide import IDE
from memory import Memory
from processor import Processor
from state import MachineState

import traceback

def catch_exceptions(t, val, tb):
    print("\n" + "!"*50)
    print("PYQT INTERCEPTED A CRASH:")
    print("!"*50)
    traceback.print_exception(t, val, tb)
    print("!"*50 + "\n")

sys.excepthook = catch_exceptions

if __name__ == "__main__":
    app = QApplication(sys.argv)
    proc = Processor()
    ram = Memory(size = 0x10000 * 2) # 64KB * 2
    state = MachineState(proc, ram)

    window = IDE(proc, ram)
    window.show()

    sys.exit(app.exec())

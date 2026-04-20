import sys

from PyQt5.QtWidgets import QApplication

from ide import IDE
from memory import Memory
from processor import Processor
from state import MachineState

if __name__ == "__main__":
    proc = Processor()
    ram = Memory(size = 0x10000 * 2) # 64KB * 2
    state = MachineState(proc, ram)

    app = QApplication(sys.argv)
    window = IDE(proc, ram)
    window.show()

    sys.exit(app.exec_())

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from processor import Processor
    from memory import Memory

@dataclass
class MachineState:
    cpu: "Processor"
    memory: "Memory"


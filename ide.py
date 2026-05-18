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

        # Define pre-written code snippets
        ide.code_snippets = {
"--- Load Example Snippet ---": "",

"1. Basic Loop":
"""; A simple loop that counts down X
    LDX #$05
LOOP:
    DEX
    BNE LOOP
    BRK
""",

"2. Memory Math":
"""; Add two numbers and store the result
    LDA #$10    ; Load 16 into A
    ADC #$14    ; Add 20
    STA $0200   ; Store result (36 / $24)
    BRK
""",

"3. Virtual Screen Draw":
    """; Fills the first 256 pixels with white
    LDA #$FF    ; Load white pixel colour
    LDX #$00    ; Start counter at 0
LOOP:
    STA $C000,X ; Store pixel to screen memory
    INX
    BNE LOOP
    BRK
""",
        "4. Indirect Addressing Test":
"""; ==========================================
; 1. Indexed Indirect: ($ZP,X)
; Reads a pointer from Zero Page, offset by X.
; ==========================================
    LDA #$50        ; We want the pointer to be $0250. 
    STA $15         ; Store low byte at ZP $15
    LDA #$02
    STA $16         ; Store high byte at ZP $16

    LDA #$AA        ; Put a secret value ($AA) at $0250
    STA $0250

    LDX #$05        ; Set X to 5
    LDA ($10,X)     ; Reads ZP $10 + X ($15). Gets pointer $0250. Loads $AA!
                    ; Check Register Panel: Accumulator should be $AA.

; ==========================================
; 2. Indirect Indexed: ($ZP),Y
; Reads a pointer from Zero Page, then adds Y.
; ==========================================
    LDA #$60        ; We want the pointer to be $0260.
    STA $20         ; Store low byte at ZP $20
    LDA #$02
    STA $21         ; Store high byte at ZP $21

    LDA #$BB        ; Put a secret value ($BB) at $0265
    STA $0265

    LDY #$05        ; Set Y to 5
    LDA ($20),Y     ; Reads ZP $20 ($0260), adds Y (5). Loads from $0265!
                    ; Check Register Panel: Accumulator should be $BB.

; ==========================================
; 3. Absolute Indirect: JMP ($LLHH)
; Jumps to the address stored at the pointer.
; ==========================================
    LDA #$40        ; We want to jump to $0240
    STA $0300       ; Store low byte at $0300
    LDA #$02
    STA $0301       ; Store high byte at $0301

    JMP ($0300)     ; Reads $0300, gets $0240, and jumps there!

; --- DEAD ZONE ---
; If the jump fails, the CPU will hit these BRKs and stop.
    BRK
    BRK
    BRK
    BRK
    BRK
    BRK
    BRK
    BRK
    BRK
    BRK
    BRK
    BRK
    BRK
    BRK
    BRK
    BRK
    BRK

; --- TARGET ZONE ($0240) ---
    LDX #$FF
    BRK
""",
"5. Disco Screen":
"""
; ==========================================
; 16-COLOUR DISCO FILL
; ==========================================

INIT:
    LDA #$10
    STA $13         

RESET_SCREEN:
    LDA #$03        
    STA $12         
    
NEXT_BANK:
    LDA $12
    STA $D000       
    LDA #$00
    STA $10         
    LDA #$80
    STA $11         
    LDY #$00       
    LDA $13         

DRAW_PAGE:
    STA ($10),Y     
    INY
    BNE DRAW_PAGE   
    
    INC $11         
    
    LDX $11         
    CPX #$C0        
    BNE DRAW_PAGE   
    
    INC $12         
    LDA $12
    CMP #$08        
    BNE NEXT_BANK   
    
FRAME_FINISHED:
    LDA $13
    CLC
    ADC #$11       
    STA $13
    
    JMP RESET_SCREEN""",
"6. Hello Innovation Fest!":
"""
; ==========================================
; Hello Innovation Fest!
; ==========================================

INIT:
    LDA #$01
    STA $14         ; Initialize starting text color in Zero Page $14

FRAME_START:
    ; ==========================================
    ; LINE 1: HELLO (Bank 4)
    ; ==========================================
    LDA #$04
    STA $D000       ; Swap to Bank 4
    LDA $14         ; Load dynamic color for this frame

    ; --- Letter H ---
    LDX #$00
L1_0:
    STA $8C94,X
    STA $8C9C,X
    STA $8DD4,X
    STA $8DDC,X
    STA $8F14,X
    STA $8F1C,X
    STA $9054,X
    STA $905C,X
    STA $9194,X
    STA $919C,X
    STA $92D4,X
    STA $92DC,X
    STA $9414,X
    STA $941C,X
    STA $9554,X
    STA $955C,X
    STA $9694,X
    STA $969C,X
    STA $9698,X
    STA $97D4,X
    STA $97DC,X
    STA $97D8,X
    STA $9914,X
    STA $991C,X
    STA $9918,X
    STA $9A54,X
    STA $9A5C,X
    STA $9A58,X
    STA $9B94,X
    STA $9B9C,X
    STA $9CD4,X
    STA $9CDC,X
    STA $9E14,X
    STA $9E1C,X
    STA $9F54,X
    STA $9F5C,X
    STA $A094,X
    STA $A09C,X
    STA $A1D4,X
    STA $A1DC,X
    STA $A314,X
    STA $A31C,X
    STA $A454,X
    STA $A45C,X
    INX
    CPX #$04
    BEQ L1_0_DONE
    JMP L1_0
L1_0_DONE:

    ; --- Letter E ---
    LDX #$00
L1_1:
    STA $8CA2,X
    STA $8CA6,X
    STA $8CAA,X
    STA $8DE2,X
    STA $8DE6,X
    STA $8DEA,X
    STA $8F22,X
    STA $8F26,X
    STA $8F2A,X
    STA $9062,X
    STA $9066,X
    STA $906A,X
    STA $91A2,X
    STA $92E2,X
    STA $9422,X
    STA $9562,X
    STA $96A2,X
    STA $96A6,X
    STA $96AA,X
    STA $97E2,X
    STA $97E6,X
    STA $97EA,X
    STA $9922,X
    STA $9926,X
    STA $992A,X
    STA $9A62,X
    STA $9A66,X
    STA $9A6A,X
    STA $9BA2,X
    STA $9CE2,X
    STA $9E22,X
    STA $9F62,X
    STA $A0A2,X
    STA $A0A6,X
    STA $A0AA,X
    STA $A1E2,X
    STA $A1E6,X
    STA $A1EA,X
    STA $A322,X
    STA $A326,X
    STA $A32A,X
    STA $A462,X
    STA $A466,X
    STA $A46A,X
    INX
    CPX #$04
    BEQ L1_1_DONE
    JMP L1_1
L1_1_DONE:

    ; --- Letter L ---
    LDX #$00
L1_2:
    STA $8CB0,X
    STA $8DF0,X
    STA $8F30,X
    STA $9070,X
    STA $91B0,X
    STA $92F0,X
    STA $9430,X
    STA $9570,X
    STA $96B0,X
    STA $97F0,X
    STA $9930,X
    STA $9A70,X
    STA $9BB0,X
    STA $9CF0,X
    STA $9E30,X
    STA $9F70,X
    STA $A0B0,X
    STA $A0B4,X
    STA $A0B8,X
    STA $A1F0,X
    STA $A1F4,X
    STA $A1F8,X
    STA $A330,X
    STA $A334,X
    STA $A338,X
    STA $A470,X
    STA $A474,X
    STA $A478,X
    INX
    CPX #$04
    BEQ L1_2_DONE
    JMP L1_2
L1_2_DONE:

    ; --- Letter L ---
    LDX #$00
L1_3:
    STA $8CBE,X
    STA $8DFE,X
    STA $8F3E,X
    STA $907E,X
    STA $91BE,X
    STA $92FE,X
    STA $943E,X
    STA $957E,X
    STA $96BE,X
    STA $97FE,X
    STA $993E,X
    STA $9A7E,X
    STA $9BBE,X
    STA $9CFE,X
    STA $9E3E,X
    STA $9F7E,X
    STA $A0BE,X
    STA $A0C2,X
    STA $A0C6,X
    STA $A1FE,X
    STA $A202,X
    STA $A206,X
    STA $A33E,X
    STA $A342,X
    STA $A346,X
    STA $A47E,X
    STA $A482,X
    STA $A486,X
    INX
    CPX #$04
    BEQ L1_3_DONE
    JMP L1_3
L1_3_DONE:

    ; --- Letter O ---
    LDX #$00
L1_4:
    STA $8CCC,X
    STA $8CD0,X
    STA $8CD4,X
    STA $8E0C,X
    STA $8E10,X
    STA $8E14,X
    STA $8F4C,X
    STA $8F50,X
    STA $8F54,X
    STA $908C,X
    STA $9090,X
    STA $9094,X
    STA $91CC,X
    STA $91D4,X
    STA $930C,X
    STA $9314,X
    STA $944C,X
    STA $9454,X
    STA $958C,X
    STA $9594,X
    STA $96CC,X
    STA $96D4,X
    STA $980C,X
    STA $9814,X
    STA $994C,X
    STA $9954,X
    STA $9A8C,X
    STA $9A94,X
    STA $9BCC,X
    STA $9BD4,X
    STA $9D0C,X
    STA $9D14,X
    STA $9E4C,X
    STA $9E54,X
    STA $9F8C,X
    STA $9F94,X
    STA $A0CC,X
    STA $A0D0,X
    STA $A0D4,X
    STA $A20C,X
    STA $A210,X
    STA $A214,X
    STA $A34C,X
    STA $A350,X
    STA $A354,X
    STA $A48C,X
    STA $A490,X
    STA $A494,X
    INX
    CPX #$04
    BEQ L1_4_DONE
    JMP L1_4
L1_4_DONE:

    ; ==========================================
    ; LINE 2: INNOVATION (Bank 5)
    ; ==========================================
    LDA #$05
    STA $D000       ; Swap to Bank 5
    LDA $14         ; Reload dynamic color

    ; --- Letter I ---
    LDX #$00
L2_0:
    STA $8C8A,X
    STA $8C8E,X
    STA $8C92,X
    STA $8DCA,X
    STA $8DCE,X
    STA $8DD2,X
    STA $8F0A,X
    STA $8F0E,X
    STA $8F12,X
    STA $904A,X
    STA $904E,X
    STA $9052,X
    STA $918E,X
    STA $92CE,X
    STA $940E,X
    STA $954E,X
    STA $968E,X
    STA $97CE,X
    STA $990E,X
    STA $9A4E,X
    STA $9B8E,X
    STA $9CCE,X
    STA $9E0E,X
    STA $9F4E,X
    STA $A08A,X
    STA $A08E,X
    STA $A092,X
    STA $A1CA,X
    STA $A1CE,X
    STA $A1D2,X
    STA $A30A,X
    STA $A30E,X
    STA $A312,X
    STA $A44A,X
    STA $A44E,X
    STA $A452,X
    INX
    CPX #$04
    BEQ L2_0_DONE
    JMP L2_0
L2_0_DONE:

    ; --- Letter N ---
    LDX #$00
L2_1:
    STA $8C98,X
    STA $8CA0,X
    STA $8DD8,X
    STA $8DE0,X
    STA $8F18,X
    STA $8F20,X
    STA $9058,X
    STA $9060,X
    STA $9198,X
    STA $919C,X
    STA $91A0,X
    STA $92D8,X
    STA $92DC,X
    STA $92E0,X
    STA $9418,X
    STA $941C,X
    STA $9420,X
    STA $9558,X
    STA $955C,X
    STA $9560,X
    STA $9698,X
    STA $969C,X
    STA $96A0,X
    STA $97D8,X
    STA $97DC,X
    STA $97E0,X
    STA $9918,X
    STA $991C,X
    STA $9920,X
    STA $9A58,X
    STA $9A5C,X
    STA $9A60,X
    STA $9B98,X
    STA $9BA0,X
    STA $9CD8,X
    STA $9CE0,X
    STA $9E18,X
    STA $9E20,X
    STA $9F58,X
    STA $9F60,X
    STA $A098,X
    STA $A0A0,X
    STA $A1D8,X
    STA $A1E0,X
    STA $A318,X
    STA $A320,X
    STA $A458,X
    STA $A460,X
    INX
    CPX #$04
    BEQ L2_1_DONE
    JMP L2_1
L2_1_DONE:

    ; --- Letter N ---
    LDX #$00
L2_2:
    STA $8CA6,X
    STA $8CAE,X
    STA $8DE6,X
    STA $8DEE,X
    STA $8F26,X
    STA $8F2E,X
    STA $9066,X
    STA $906E,X
    STA $91A6,X
    STA $91AA,X
    STA $91AE,X
    STA $92E6,X
    STA $92EA,X
    STA $92EE,X
    STA $9426,X
    STA $942A,X
    STA $942E,X
    STA $9566,X
    STA $956A,X
    STA $956E,X
    STA $96A6,X
    STA $96AA,X
    STA $96AE,X
    STA $97E6,X
    STA $97EA,X
    STA $97EE,X
    STA $9926,X
    STA $992A,X
    STA $992E,X
    STA $9A66,X
    STA $9A6A,X
    STA $9A6E,X
    STA $9BA6,X
    STA $9BAE,X
    STA $9CE6,X
    STA $9CEE,X
    STA $9E26,X
    STA $9E2E,X
    STA $9F66,X
    STA $9F6E,X
    STA $A0A6,X
    STA $A0AE,X
    STA $A1E6,X
    STA $A1EE,X
    STA $A326,X
    STA $A32E,X
    STA $A466,X
    STA $A46E,X
    INX
    CPX #$04
    BEQ L2_2_DONE
    JMP L2_2
L2_2_DONE:

    ; --- Letter O ---
    LDX #$00
L2_3:
    STA $8CB4,X
    STA $8CB8,X
    STA $8CBC,X
    STA $8DF4,X
    STA $8DF8,X
    STA $8DFC,X
    STA $8F34,X
    STA $8F38,X
    STA $8F3C,X
    STA $9074,X
    STA $9078,X
    STA $907C,X
    STA $91B4,X
    STA $91BC,X
    STA $92F4,X
    STA $92FC,X
    STA $9434,X
    STA $943C,X
    STA $9574,X
    STA $957C,X
    STA $96B4,X
    STA $96BC,X
    STA $97F4,X
    STA $97FC,X
    STA $9934,X
    STA $993C,X
    STA $9A74,X
    STA $9A7C,X
    STA $9BB4,X
    STA $9BBC,X
    STA $9CF4,X
    STA $9CFC,X
    STA $9E34,X
    STA $9E3C,X
    STA $9F74,X
    STA $9F7C,X
    STA $A0B4,X
    STA $A0B8,X
    STA $A0BC,X
    STA $A1F4,X
    STA $A1F8,X
    STA $A1FC,X
    STA $A334,X
    STA $A338,X
    STA $A33C,X
    STA $A474,X
    STA $A478,X
    STA $A47C,X
    INX
    CPX #$04
    BEQ L2_3_DONE
    JMP L2_3
L2_3_DONE:

    ; --- Letter V ---
    LDX #$00
L2_4:
    STA $8CC2,X
    STA $8CCA,X
    STA $8E02,X
    STA $8E0A,X
    STA $8F42,X
    STA $8F4A,X
    STA $9082,X
    STA $908A,X
    STA $91C2,X
    STA $91CA,X
    STA $9302,X
    STA $930A,X
    STA $9442,X
    STA $944A,X
    STA $9582,X
    STA $958A,X
    STA $96C2,X
    STA $96CA,X
    STA $9802,X
    STA $980A,X
    STA $9942,X
    STA $994A,X
    STA $9A82,X
    STA $9A8A,X
    STA $9BC2,X
    STA $9BCA,X
    STA $9D02,X
    STA $9D0A,X
    STA $9E42,X
    STA $9E4A,X
    STA $9F82,X
    STA $9F8A,X
    
    ; --- THE FIXED BOTTOM POINT OF THE V ---
    STA $A0C6,X
    STA $A206,X
    STA $A346,X
    STA $A486,X
    ; ---------------------------------------

    INX
    CPX #$04
    BEQ L2_4_DONE
    JMP L2_4
L2_4_DONE:

    ; --- Letter A ---
    LDX #$00
L2_5:
    STA $8CD4,X
    STA $8E14,X
    STA $8F54,X
    STA $9094,X
    STA $91D0,X
    STA $91D8,X
    STA $9310,X
    STA $9318,X
    STA $9450,X
    STA $9458,X
    STA $9590,X
    STA $9598,X
    STA $96D0,X
    STA $96D4,X
    STA $96D8,X
    STA $9810,X
    STA $9814,X
    STA $9818,X
    STA $9950,X
    STA $9954,X
    STA $9958,X
    STA $9A90,X
    STA $9A94,X
    STA $9A98,X
    STA $9BD0,X
    STA $9BD8,X
    STA $9D10,X
    STA $9D18,X
    STA $9E50,X
    STA $9E58,X
    STA $9F90,X
    STA $9F98,X
    STA $A0D0,X
    STA $A0D8,X
    STA $A210,X
    STA $A218,X
    STA $A350,X
    STA $A358,X
    STA $A490,X
    STA $A498,X
    INX
    CPX #$04
    BEQ L2_5_DONE
    JMP L2_5
L2_5_DONE:

    ; --- Letter T ---
    LDX #$00
L2_6:
    STA $8CDE,X
    STA $8CE2,X
    STA $8CE6,X
    STA $8E1E,X
    STA $8E22,X
    STA $8E26,X
    STA $8F5E,X
    STA $8F62,X
    STA $8F66,X
    STA $909E,X
    STA $90A2,X
    STA $90A6,X
    STA $91E2,X
    STA $9322,X
    STA $9462,X
    STA $95A2,X
    STA $96E2,X
    STA $9822,X
    STA $9962,X
    STA $9AA2,X
    STA $9BE2,X
    STA $9D22,X
    STA $9E62,X
    STA $9FA2,X
    STA $A0E2,X
    STA $A222,X
    STA $A362,X
    STA $A4A2,X
    INX
    CPX #$04
    BEQ L2_6_DONE
    JMP L2_6
L2_6_DONE:

    ; --- Letter I ---
    LDX #$00
L2_7:
    STA $8CEC,X
    STA $8CF0,X
    STA $8CF4,X
    STA $8E2C,X
    STA $8E30,X
    STA $8E34,X
    STA $8F6C,X
    STA $8F70,X
    STA $8F74,X
    STA $90AC,X
    STA $90B0,X
    STA $90B4,X
    STA $91F0,X
    STA $9330,X
    STA $9470,X
    STA $95B0,X
    STA $96F0,X
    STA $9830,X
    STA $9970,X
    STA $9AB0,X
    STA $9BF0,X
    STA $9D30,X
    STA $9E70,X
    STA $9FB0,X
    STA $A0EC,X
    STA $A0F0,X
    STA $A0F4,X
    STA $A22C,X
    STA $A230,X
    STA $A234,X
    STA $A36C,X
    STA $A370,X
    STA $A374,X
    STA $A4AC,X
    STA $A4B0,X
    STA $A4B4,X
    INX
    CPX #$04
    BEQ L2_7_DONE
    JMP L2_7
L2_7_DONE:

    ; --- Letter O ---
    LDX #$00
L2_8:
    STA $8CFA,X
    STA $8CFE,X
    STA $8D02,X
    STA $8E3A,X
    STA $8E3E,X
    STA $8E42,X
    STA $8F7A,X
    STA $8F7E,X
    STA $8F82,X
    STA $90BA,X
    STA $90BE,X
    STA $90C2,X
    STA $91FA,X
    STA $9202,X
    STA $933A,X
    STA $9342,X
    STA $947A,X
    STA $9482,X
    STA $95BA,X
    STA $95C2,X
    STA $96FA,X
    STA $9702,X
    STA $983A,X
    STA $9842,X
    STA $997A,X
    STA $9982,X
    STA $9ABA,X
    STA $9AC2,X
    STA $9BFA,X
    STA $9C02,X
    STA $9D3A,X
    STA $9D42,X
    STA $9E7A,X
    STA $9E82,X
    STA $9FBA,X
    STA $9FC2,X
    STA $A0FA,X
    STA $A0FE,X
    STA $A102,X
    STA $A23A,X
    STA $A23E,X
    STA $A242,X
    STA $A37A,X
    STA $A37E,X
    STA $A382,X
    STA $A4BA,X
    STA $A4BE,X
    STA $A4C2,X
    INX
    CPX #$04
    BEQ L2_8_DONE
    JMP L2_8
L2_8_DONE:

    ; --- Letter N ---
    LDX #$00
L2_9:
    STA $8D08,X
    STA $8D10,X
    STA $8E48,X
    STA $8E50,X
    STA $8F88,X
    STA $8F90,X
    STA $90C8,X
    STA $90D0,X
    STA $9208,X
    STA $920C,X
    STA $9210,X
    STA $9348,X
    STA $934C,X
    STA $9350,X
    STA $9488,X
    STA $948C,X
    STA $9490,X
    STA $95C8,X
    STA $95CC,X
    STA $95D0,X
    STA $9708,X
    STA $970C,X
    STA $9710,X
    STA $9848,X
    STA $984C,X
    STA $9850,X
    STA $9988,X
    STA $998C,X
    STA $9990,X
    STA $9AC8,X
    STA $9ACC,X
    STA $9AD0,X
    STA $9C08,X
    STA $9C10,X
    STA $9D48,X
    STA $9D50,X
    STA $9E88,X
    STA $9E90,X
    STA $9FC8,X
    STA $9FD0,X
    STA $A108,X
    STA $A110,X
    STA $A248,X
    STA $A250,X
    STA $A388,X
    STA $A390,X
    STA $A4C8,X
    STA $A4D0,X
    INX
    CPX #$04
    BEQ L2_9_DONE
    JMP L2_9
L2_9_DONE:

    ; ==========================================
    ; LINE 3: FEST! (Bank 6)
    ; ==========================================
    LDA #$06
    STA $D000       ; Swap to Bank 6
    LDA $14         ; Reload dynamic color

    ; --- Letter F ---
    LDX #$00
L3_0:
    STA $8C94,X
    STA $8C98,X
    STA $8C9C,X
    STA $8DD4,X
    STA $8DD8,X
    STA $8DDC,X
    STA $8F14,X
    STA $8F18,X
    STA $8F1C,X
    STA $9054,X
    STA $9058,X
    STA $905C,X
    STA $9194,X
    STA $92D4,X
    STA $9414,X
    STA $9554,X
    STA $9694,X
    STA $9698,X
    STA $97D4,X
    STA $97D8,X
    STA $9914,X
    STA $9918,X
    STA $9A54,X
    STA $9A58,X
    STA $9B94,X
    STA $9CD4,X
    STA $9E14,X
    STA $9F54,X
    STA $A094,X
    STA $A1D4,X
    STA $A314,X
    STA $A454,X
    INX
    CPX #$04
    BEQ L3_0_DONE
    JMP L3_0
L3_0_DONE:

    ; --- Letter E ---
    LDX #$00
L3_1:
    STA $8CA2,X
    STA $8CA6,X
    STA $8CAA,X
    STA $8DE2,X
    STA $8DE6,X
    STA $8DEA,X
    STA $8F22,X
    STA $8F26,X
    STA $8F2A,X
    STA $9062,X
    STA $9066,X
    STA $906A,X
    STA $91A2,X
    STA $92E2,X
    STA $9422,X
    STA $9562,X
    STA $96A2,X
    STA $96A6,X
    STA $96AA,X
    STA $97E2,X
    STA $97E6,X
    STA $97EA,X
    STA $9922,X
    STA $9926,X
    STA $992A,X
    STA $9A62,X
    STA $9A66,X
    STA $9A6A,X
    STA $9BA2,X
    STA $9CE2,X
    STA $9E22,X
    STA $9F62,X
    STA $A0A2,X
    STA $A0A6,X
    STA $A0AA,X
    STA $A1E2,X
    STA $A1E6,X
    STA $A1EA,X
    STA $A322,X
    STA $A326,X
    STA $A32A,X
    STA $A462,X
    STA $A466,X
    STA $A46A,X
    INX
    CPX #$04
    BEQ L3_1_DONE
    JMP L3_1
L3_1_DONE:

    ; --- Letter S ---
    LDX #$00
L3_2:
    STA $8CB0,X
    STA $8CB4,X
    STA $8CB8,X
    STA $8DF0,X
    STA $8DF4,X
    STA $8DF8,X
    STA $8F30,X
    STA $8F34,X
    STA $8F38,X
    STA $9070,X
    STA $9074,X
    STA $9078,X
    STA $91B0,X
    STA $92F0,X
    STA $9430,X
    STA $9570,X
    STA $96B0,X
    STA $96B4,X
    STA $96B8,X
    STA $97F0,X
    STA $97F4,X
    STA $97F8,X
    STA $9930,X
    STA $9934,X
    STA $9938,X
    STA $9A70,X
    STA $9A74,X
    STA $9A78,X
    STA $9BB8,X
    STA $9CF8,X
    STA $9E38,X
    STA $9F78,X
    STA $A0B0,X
    STA $A0B4,X
    STA $A0B8,X
    STA $A1F0,X
    STA $A1F4,X
    STA $A1F8,X
    STA $A330,X
    STA $A334,X
    STA $A338,X
    STA $A470,X
    STA $A474,X
    STA $A478,X
    INX
    CPX #$04
    BEQ L3_2_DONE
    JMP L3_2
L3_2_DONE:

    ; --- Letter T ---
    LDX #$00
L3_3:
    STA $8CBE,X
    STA $8CC2,X
    STA $8CC6,X
    STA $8DFE,X
    STA $8E02,X
    STA $8E06,X
    STA $8F3E,X
    STA $8F42,X
    STA $8F46,X
    STA $907E,X
    STA $9082,X
    STA $9086,X
    STA $91C2,X
    STA $9302,X
    STA $9442,X
    STA $9582,X
    STA $96C2,X
    STA $9802,X
    STA $9942,X
    STA $9A82,X
    STA $9BC2,X
    STA $9D02,X
    STA $9E42,X
    STA $9F82,X
    STA $A0C2,X
    STA $A202,X
    STA $A342,X
    STA $A482,X
    INX
    CPX #$04
    BEQ L3_3_DONE
    JMP L3_3
L3_3_DONE:

    ; --- Letter ! ---
    LDX #$00
L3_4:
    STA $8CD0,X
    STA $8E10,X
    STA $8F50,X
    STA $9090,X
    STA $91D0,X
    STA $9310,X
    STA $9450,X
    STA $9590,X
    STA $96D0,X
    STA $9810,X
    STA $9950,X
    STA $9A90,X
    STA $A0D0,X
    STA $A210,X
    STA $A350,X
    STA $A490,X
    INX
    CPX #$04
    BEQ L3_4_DONE
    JMP L3_4
L3_4_DONE:

    ; ==========================================
    ; PHASE 4: TIME DELAY (Burn CPU Cycles)
    ; ==========================================
    ; Adjust #$06 up or down to change the speed of the color cycle
    LDA #$06        
    STA $16

DELAY_OUTER:
    LDA #$FF
    STA $15

DELAY_INNER:
    DEC $15
    BNE DELAY_INNER
    DEC $16
    BNE DELAY_OUTER

    ; ==========================================
    ; PHASE 5: SHIFT COLOR & REPEAT
    ; ==========================================
    
    ; Shift Text Color by a prime offset to bounce through the palette
    LDA $14
    CLC
    ADC #$1D
    STA $14

    JMP FRAME_START ; Loop infinitely!
"""
        }

        # Snippet drop-down menu
        ide.snippet_selector = QComboBox()
        ide.snippet_selector.addItems(ide.code_snippets.keys())
        ide.snippet_selector.setMinimumWidth(200)

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
        ide.speed_slider.setRange(1, 5000)  # 1 to 50 instructions per frame
        ide.speed_slider.setValue(1)  # Default to slowest
        ide.speed_slider.setMinimumWidth(100)

        ide.load_button.clicked.connect(ide.load_code)
        ide.run_button.clicked.connect(ide.toggle_execution)
        ide.step_forward_button.clicked.connect(ide.step_forward)
        ide.step_back_button.clicked.connect(ide.step_backward)
        ide.toggle_registers_button.clicked.connect(ide.toggle_registers)
        ide.toggle_memory_button.clicked.connect(ide.toggle_memory_map)
        ide.snippet_selector.currentIndexChanged.connect(ide.load_snippet)

        # Top bar for the snippet selector
        top_bar_layout = QHBoxLayout()
        top_bar_layout.addWidget(QLabel("Code Examples:"))
        top_bar_layout.addWidget(ide.snippet_selector)
        top_bar_layout.addStretch()

        editor_layout.addLayout(top_bar_layout)
        editor_layout.addWidget(ide.editor)
        editor_layout.addLayout(button_layout)

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

        ide.screen_timer = QTimer()
        ide.screen_timer.timeout.connect(ide.refresh_screen)
        ide.screen_timer.start(16)

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

    def load_snippet(ide: 'IDE') -> None:
        """
        Loads the selected pre-written code into the editor.
        """
        selected_title = ide.snippet_selector.currentText()
        snippet_code = ide.code_snippets.get(selected_title, "")
        if snippet_code:
            ide.editor.setPlainText(snippet_code)
            ide.log_to_console(f"Loaded snippet: {selected_title}")

            ide.snippet_selector.setCurrentIndex(0)

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
    def refresh_screen(ide: 'IDE') -> None:
        """Only draws the screen 60 times a second, regardless of CPU speed."""
        if ide.state.memory.screen_refresh:
            ide.vscreen.render()
            ide.state.memory.screen_refresh = False

    @safe_execution
    def emulator_tick(ide : 'ide') -> None:
        batch_size = ide.speed_slider.value()

        for _ in range(batch_size):
            ide.processor.fetch_decode_execute(ide.state)

        if ide.register_panel.isVisible():
            ide.update_register_display()

        if ide.memory_panel.isVisible():
            ide.update_memory_display()

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

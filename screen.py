import struct

import PyQt6
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QImage, QPixmap

from memory import Memory
from PyQt6.QtWidgets import QLabel


class Screen(QLabel):
    def __init__(screen : 'Screen', memory : Memory, vmem_start: int = 49152) -> None:
        """
        :param mem: Reference to memory module
        :param vmem_start: Start address of video memory (Bank 3 up to Bank 8)
        """
        super().__init__()

        screen.width = 320
        screen.height = 240
        screen.scale_factor = 2
        screen.vmem_start = vmem_start
        screen.memory = memory

        screen.setFixedSize(screen.width * screen.scale_factor,
                            screen.height * screen.scale_factor)
        screen.setStyleSheet("background-color: black;")

        screen.color_lut = []
        for byte in range(256):
            red_bits = (byte >> 5) & 0b111
            green_bits = (byte >> 2) & 0b111
            blue_bits = byte & 0b00000011

            red = int(red_bits * (255 / 7))
            green = int(green_bits * (255 / 7))
            blue = int(blue_bits * (255 / 3))

            # Pack directly into raw 4-byte RGBA chunks
            screen.color_lut.append(struct.pack('BBBB', red, green, blue, 255))

    '''
    def colour_decode(screen : 'Screen', byte : int) -> QColor:
        """Converts an 8-bit value into a 24-bit RGB tuple

        """
        red_bits = (byte >> 5) & 0b111
        green_bits = (byte >> 2) & 0b111
        blue_bits = byte & 0b00000011

        red = int(red_bits * (255 / 7))
        green = int(green_bits * (255 / 7))
        blue = int(blue_bits * (255 / 3))

        return QColor(red, green, blue)
    '''

    def render(screen : 'Screen') -> None:
        """
        # pixel_array = pygame.PixelArray(screen.screen)

        image = QImage(screen.width, screen.height, QImage.Format.Format_RGB32)
        mem_index = screen.vmem_start

        for y in range(screen.height):
            for x in range(screen.width):
                colour_byte = screen.memory.memory[mem_index]
                rgb = screen.colour_decode(colour_byte)
                image.setPixelColor(x, y, rgb)

                mem_index += 1

        pixmap = QPixmap.fromImage(image).scaled(
            screen.width * screen.scale_factor,
            screen.height * screen.scale_factor,
            PyQt6.QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            PyQt6.QtCore.Qt.TransformationMode.FastTransformation,
        )

        screen.setPixmap(pixmap)
        """

        vmem_end = screen.vmem_start + (screen.width * screen.height)
        screen_memory = screen.memory.memory[screen.vmem_start: vmem_end]

        lut = screen.color_lut
        raw_bytes = b''.join(lut[byte] for byte in screen_memory)

        # 3. Create a QImage directly from the raw byte stream
        image = QImage(raw_bytes, screen.width, screen.height, QImage.Format.Format_RGBA8888)

        # 4. Scale it up so it looks chunky and retro, then apply it to the label!
        scaled_image = image.scaled(screen.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                    Qt.TransformationMode.FastTransformation)
        screen.setPixmap(QPixmap.fromImage(scaled_image))
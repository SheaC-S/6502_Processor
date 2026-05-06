class Memory:
    def __init__(mem : 'Memory', size: int = 65536) -> None:
        """
        Initialise the memory

        :param size: size of the memory available:
        :return: None
        """
        if size < 0x0200:
            raise ValueError("Memory size is too small for CPU to function")

        mem.size = size
        mem.memory = [0] * mem.size

        mem.is_banked = size > 0xFFFF
        mem.screen_refresh = True

        if mem.is_banked:
            mem.bank_size = 16 * 1024
            mem.window_start = 0x8000
            mem.window_end = 0xBFFF
            mem.bank_register = 0xD000

            mem.current_bank = 0
            mem.max_banks = mem.size // mem.bank_size

    def translate_address(mem, address: int) -> int:
        """
        Translates memory addresses beyond the 16-bit address space into a physical memory address.

        :param mem: The memory module
        :param address: The logical address to translate into a physical address
        """

        if not mem.is_banked:
            return address

        if mem.window_start <= address < mem.window_end:
            offset = address - mem.window_start
            physical_address = (mem.current_bank * mem.bank_size) + offset
            return physical_address

        return address

    def __getitem__(mem : 'Memory', address: int) -> int:
        """
        Get the value at given address

        :param address: The address to read from
        :return: The value at given address
        """
        if 0x0000 > address or mem.size <= address:
            raise ValueError("Memory address is not valid")

        if mem.is_banked and address == mem.bank_register:
            return mem.memory[address]

        physical_address = mem.translate_address(address)
        return mem.memory[physical_address]

    def __setitem__(mem : 'Memory', address: int, value: int) -> int:
        """
        Set the value at given address

        :param address: The address to write to
        :param value: The value ot write to the address
        :return: None
        """
        if 0x0000 > address or mem.size <= address:
            raise ValueError("Memory address is not valid")
        if value.bit_length() > 8:
            raise ValueError("Value too large")

        if mem.is_banked and address == mem.bank_register:
            mem.current_bank = value % mem.max_banks
            return mem.current_bank

        physical_address = mem.translate_address(address)
        mem.memory[physical_address] = value
        return mem.memory[physical_address]

if __name__ == "__main__":
    m = Memory(0x1FFFF)

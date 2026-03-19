class Memory:
    def __init__(self, size: int = 65536) -> None:
        """
        Initialise the memory

        :param size: size of the memory available:
        :return: None
        """
        if 0x0200 < (size - 1) > 0xFFFF:
            raise ValueError("Memory size is not valid")
        self.size = size
        self.memory = [0] * self.size
        print(len(self.memory))

    def __getitem__(self, address: int) -> int:
        """
        Get the value at given address

        :param address: The address to read from
        :return: The value at given address
        """
        if 0x0000 < address > self.size:
            raise ValueError("Memory address is not valid")
        return self.memory[address]

    def __setitem__(self, address: int, value: int) -> int:
        """
        Set the value at given address

        :param address: The address to write to
        :param value: The value ot write to the address
        :return: None
        """
        if 0x0000 < address > self.size:
            raise ValueError("Memory address is not valid")
        if value.bit_length() > 8:
            raise ValueError("Value too large")
        self.memory[address] = value
        return self.memory[address]

if __name__ == "__main__":
    m = Memory()

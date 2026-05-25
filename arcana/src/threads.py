import logging

logging.basicConfig(
    filename='error.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class Thread:
    def __init__(self, name, frequency, stability):
        self.__name = name
        self.frequency = frequency
        self.stability = stability

    @property
    def name(self):
        return self.__name

    @property
    def frequency(self):
        return self.__frequency

    @frequency.setter
    def frequency(self, value):
        if not (0.1 <= value <= 999.9):
            logging.error(f"Invalid frequency: {value}")
            raise ValueError(f"Frequency must be between 0.1 and 999.9, got {value}")
        self.__frequency = value

    @property
    def stability(self):
        return self.__stability

    @stability.setter
    def stability(self, value):
        if not (0.0 <= value <= 1.0):
            logging.error(f"Invalid stability: {value}")
            raise ValueError(f"Stability must be between 0.0 and 1.0, got {value}")
        self.__stability = value

    def resonate(self, other):
        return (self.__frequency + other.frequency) * (self.__stability * other.stability)

    def __add__(self, other):
        new_freq = min((self.__frequency + other.frequency) / 2, 999.9)
        new_stab = (self.__stability + other.stability) / 2
        return Thread(f"{self.__name}+{other.name}", new_freq, new_stab)

    def __str__(self):
        return f"Thread({self.__name}, freq={self.__frequency}, stab={self.__stability})"

    def __repr__(self):
        return f"Thread(name={self.__name!r}, frequency={self.__frequency}, stability={self.__stability})"


class EnergyThread(Thread):
    def __init__(self, name, frequency, stability, power):
        super().__init__(name, frequency, stability)
        self.power = power

    def resonate(self, other):
        base = super().resonate(other)
        return base * self.power

    def __str__(self):
        return f"EnergyThread({self.name}, power={self.power})"


class FormThread(Thread):
    def __init__(self, name, frequency, stability, shape):
        super().__init__(name, frequency, stability)
        self.shape = shape

    def resonate(self, other):
        base = super().resonate(other)
        return base + len(self.shape)

    def __str__(self):
        return f"FormThread({self.name}, shape={self.shape})"


class TimeThread(Thread):
    def __init__(self, name, frequency, stability, epoch):
        super().__init__(name, frequency, stability)
        self.epoch = epoch

    def resonate(self, other):
        base = super().resonate(other)
        return base / (self.epoch + 1)

    def __str__(self):
        return f"TimeThread({self.name}, epoch={self.epoch})"

import time
from machine import Pin

class HX711:
    def __init__(self, pd_sck, dout, gain=128):
        self.pSCK = pd_sck
        self.pDOUT = dout
        self.pSCK.value(False)
        self.GAIN = 0
        self.OFFSET = 0
        self.SCALE = 1
        self.time_constant = 0.1
        self.set_gain(gain)

    def set_gain(self, gain):
        if gain is 128:
            self.GAIN = 1
        elif gain is 64:
            self.GAIN = 3
        elif gain is 32:
            self.GAIN = 2

        self.pSCK.value(False)
        self.read()

    def is_ready(self):
        return self.pDOUT.value() == 0

    def read(self):
        # wait for the device to be ready
        # for i in range(500):
        #     if self.pDOUT.value() == 0:
        #         break
        #     time.sleep_ms(1)
        
        # if self.pDOUT.value() == 1:
        #     raise OSError("HX711 not ready")

        # count = 0
        # for i in range(24):
        #     self.pSCK.value(True)
        #     self.pSCK.value(False)
        #     count = count << 1
        #     if self.pDOUT.value():
        #         count += 1

        # self.pSCK.value(True)
        # count = count ^ 0x800000
        # self.pSCK.value(False)

        # for i in range(self.GAIN):
        #     self.pSCK.value(True)
        #     self.pSCK.value(False)

        # return count
        
        # Simplified read for stability
        count = 0
        while self.pDOUT.value():
            pass

        for i in range(24):
            self.pSCK.value(True)
            count = count << 1
            self.pSCK.value(False)
            if self.pDOUT.value():
                count += 1

        self.pSCK.value(True)
        count = count ^ 0x800000
        self.pSCK.value(False)

        for i in range(self.GAIN):
            self.pSCK.value(True)
            self.pSCK.value(False)

        return count

    def read_average(self, times=3):
        sum = 0
        for i in range(times):
            sum += self.read()
        return sum / times

    def get_value(self):
        return self.read_average(1) - self.OFFSET

    def get_units(self):
        return self.get_value() / self.SCALE

    def tare(self, times=15):
        sum = self.read_average(times)
        self.set_offset(sum)

    def set_scale(self, scale):
        self.SCALE = scale

    def set_offset(self, offset):
        self.OFFSET = offset

    def power_down(self):
        self.pSCK.value(False)
        self.pSCK.value(True)

    def power_up(self):
        self.pSCK.value(False)


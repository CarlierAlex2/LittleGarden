import spidev
from RPi import GPIO

class Mcp:
    def __init__(self):
        self.byte_start = 1
        self.byte_channel = 128 # 0b10000000
        self.byte_end = 0
        self.spi = spidev.SpiDev()
        self.spi.open(0,0) #bus SPIO, slave op CE 0
        self.spi.max_speed_hz = 10**5 #10kHz

    def read_channel(self, channel):
        channel_byte = channel << 4
        send_byte = channel_byte | self.byte_channel
        #print(f"channel {bin(send_byte)}")
        byte_array = [self.byte_start, send_byte, self.byte_end]

        response = self.spi.xfer(byte_array)

        waarde = response[1] & 3 # response[1] & 0b00000011 => hou de laatste 2 bits over van de waarde
        waarde = waarde << 8 # schuif naar positie 9 en 10
        waarde = waarde | response[2] # voeg de 2 bits en 8 bits samen tot 10 bits

        return waarde

    def closepi(self):
        self.spi.close()
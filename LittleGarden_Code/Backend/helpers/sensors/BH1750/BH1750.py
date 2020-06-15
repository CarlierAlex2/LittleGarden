from smbus import SMBus
import time


class BH1750:
    def __init__(self):
        self.slave_address = 0x23
        self.power_down_instruct = 0x00
        self.power_up_instruct = 0x01
        self.reset_instruct = 0x07 # Reset data register value
        self.resolution = 0

        self.set_resolution(0)

        self.i2c = SMBus() #initialize library
        self.i2c.open(1) # open bus1


    def set_resolution(self, modus, isContinuous = True): #set used resolution
        resolution_array = [0x13, 0x10, 0x11]
        if isContinuous == False: # instructions where device powers down after 1 measurement
            resolution_array = [0x23, 0x20, 0x21]

        if modus < len(resolution_array) and modus >= 0:
            self.resolution = resolution_array[modus]

        # 0 = 4lx resolution. Time typically 16ms.
        # 1 = 1lx resolution. Time typically 120ms
        # 2 = 0.5lx resolution. Time typically 120ms
 

    def data_to_number(self, data):     # convert 2 bytes of data into a decimal number
        return ((data[1] + (256 * data[0])) / 1.2)


    def reset(self):
        self.i2c.write_byte_data(self.slave_address, self.reset_instruct)
    

    def read_light(self):
        data = self.i2c.read_i2c_block_data(self.slave_address, self.resolution, 2)
        time.sleep(0.1)
        #self.reset()
        return self.data_to_number(data)
from RPi import GPIO
import time

max_percent = 70

class Soil_Sensor:
    def __init__(self, channel, mcp):
        self.channel = channel
        self.mcp = mcp

    def read_soilwater_waarde(self):
        waarde = 1023 - self.mcp.read_channel(self.channel)
        return waarde

    def read_soilwater_percentage(self):
        waarde = self.read_soilwater_waarde()
        waarde = (waarde / 1023.0) * 100
        waarde = (waarde / max_percent) * 100
        return waarde

    def close_Sensor(self):
        self.mcp.closepi()

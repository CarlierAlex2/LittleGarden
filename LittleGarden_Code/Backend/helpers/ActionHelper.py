from .Actuators.Relay import Relay

from datetime import datetime
import time

from flask import jsonify


class ActionHelper:
    def __init__(self, water_pin, light_pin):
        self.actuator_water = Relay(water_pin, "Water pump")
        self.actuator_light = Relay(light_pin, "LED strip")

    def toggle_actuator(self, actuatorType):
        if(actuatorType == "water"):
            isActive = self.actuator_water.toggle()
            return isActive
        if(actuatorType == "light"):
            isActive = self.actuator_light.toggle()
            return isActive
        return None

    def is_actuator_active(self, actuatorType):
        if(actuatorType == "water"):
            isActive = self.actuator_water.getActiveState()
            return isActive
        if(actuatorType == "light"):
            isActive = self.actuator_light.getActiveState()
            return isActive
        return None


    def set_active(self, actuatorType, status):
        if(actuatorType == "water"):
            return self.actuator_water.setActive(status)
        if(actuatorType == "light"):
            return self.actuator_light.setActive(status)

    def stop(self):
        self.set_active("water", False)
        self.set_active("light", False)




from RPi import GPIO

class Relay:
    def __init__(self, pin, name_relay):
        self.pin = pin
        self.name = name_relay
        GPIO.setup(pin,GPIO.OUT)

        self.isActive = False
        self.setActive(self.isActive)


    def toggle(self):
        isActive = not self.isActive
        return self.setActive(isActive)

    def setActive(self, isActive):
        name = str(self.name)
        if (isActive == True):
            GPIO.output(self.pin,GPIO.HIGH)
            print(f"{name} is ACTIVED")
        else:
            GPIO.output(self.pin,GPIO.LOW)
            print(f"{name} is DEACTIVATED")
        print("")
        self.isActive = isActive
        return isActive

    def getActiveState(self):
        return self.isActive
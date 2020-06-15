from RPi import GPIO
import time

from .PCF8574 import PCF8574

class LCD_PCF:
    def __init__(self, SDA, SCL, E, RS, address=56, reversedPins = False, isVierBits=False):
        self.__pcf8574 = PCF8574(SDA, SCL, address, 0.00001, reversedPins)

        self.__shortDelay = 0.00001
        self.__longDelay = 0.00002
        self.__scrollDelay = 0.6
        self._isVierBits = isVierBits

        self.__isDisplayOn = True
        self.__isCursorOn = True
        self.__isCursorBlinkOn = False

        self.__instructScrollLeft = 0x18
        self.__instructScrollRight = 0x1C

        self.__shiftCursorLeft = 0x10
        self.__shiftCursorRight = 0x14

        self.RS_pin = RS
        self.E_pin = E

        self.__initGPIO()


    @property
    def displayOn(self):
        return self.__isDisplayOn

    @displayOn.setter
    def displayOn(self, value: bool):
        self.__isDisplayOn = value

    @property
    def cursorOn(self):
        return self.__isCursorOn

    @cursorOn.setter
    def cursorOn(self, value: bool):
        self.__isCursorOn = value

    @property
    def cursorBlink(self):
        return self.__isCursorBlinkOn

    @cursorBlink.setter
    def cursorBlink(self, value: bool):
        self.__isCursorBlinkOn = value



    def __initGPIO(self):
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.RS_pin, GPIO.OUT)
        GPIO.setup(self.E_pin, GPIO.OUT)

        GPIO.output(self.E_pin, GPIO.HIGH)



    def __checkParameterDisplay(self, bool_waarde, display_instructie):
        if bool_waarde == True:
            display_instructie = (display_instructie << 1) | 1
        else:
            display_instructie = (display_instructie << 1) | 0
        return display_instructie


    def init_LCD(self):
        functionSet = 0b00111000
        #print(f"Instructie: ${bin(functionSet)}")
        self.__send_instruction(functionSet) #function set

        display_instructie = 0b00001
        display_instructie = self.__checkParameterDisplay(self.__isDisplayOn, display_instructie)
        display_instructie = self.__checkParameterDisplay(self.__isCursorOn, display_instructie)
        display_instructie = self.__checkParameterDisplay(self.__isCursorBlinkOn, display_instructie)
        #print(f"Instructie: ${bin(display_instructie)}")
        self.__send_instruction(display_instructie) #display, cursor en blink on

        clearDisplay = 0b00000001
        #print(f"Instructie: ${bin(clearDisplay)}")
        self.__send_instruction(clearDisplay) #clear display en cursor home


    def reset_LCD(self):
        self.__send_instruction(0x01)

    def clear_LCD(self):
        self.__send_instruction(0x01)


    def __set_data_bits(self, byte):
        #print(bin(byte))
        self.__pcf8574.write_outputs(int(byte))


    def __send_instruction(self, waarde):
        GPIO.output(self.RS_pin, GPIO.LOW) # instellen op instructies

        self.__set_data_bits(waarde)
        time.sleep(self.__shortDelay)

        GPIO.output(self.E_pin, GPIO.LOW)
        time.sleep(self.__shortDelay)
        GPIO.output(self.E_pin, GPIO.HIGH)

        time.sleep(self.__longDelay)


    def __send_character(self, waarde):
        GPIO.output(self.RS_pin, GPIO.HIGH) # instellen op tekst

        self.__set_data_bits(waarde)
        time.sleep(self.__shortDelay)
        
        GPIO.output(self.E_pin, GPIO.LOW)
        time.sleep(self.__shortDelay)
        GPIO.output(self.E_pin, GPIO.HIGH)

        time.sleep(self.__longDelay)


    def __set_ddram(self, waarde_positie):
        positie = int(waarde_positie)
        ddram = int(128)
        instructie = ddram | positie
        self.__send_instruction(instructie)


    def second_row(self):
        self.__set_ddram(0x40)


    def writeA(self):
        self.__send_character(65)


    def write_message(self, message):
        lengte_scroll = 32
        lengte_bericht = len(message)
        #print(lengte_bericht)

        if lengte_bericht > lengte_scroll:
            self.__write_message_scroll(message)
        else:
            self.__write_message_default(message)

    
    def __write_message_default(self, message):
        max_lengte = 16
        lengte_bericht = len(message)

        lijn_1 = message[0:max_lengte]
        lijn_2 = ""
        next_line_index = lijn_1.rfind(' ')

        if next_line_index >= 0 and lengte_bericht > max_lengte:
            lijn_1 = lijn_1[0:next_line_index]
            lijn_2 = message[next_line_index + 1:]

        len1 = len(lijn_1)
        len2 = len(lijn_2)

        self.__write_tekst(lijn_1, len1)
        if(len2 >= 2):
            self.second_row()
            self.__write_tekst(lijn_2, len2)


    def __write_message_scroll(self, message):
        lengte_bericht = len(message)
        self.__write_tekst(message, lengte_bericht)
        lengte_scroll = lengte_bericht + 6
        for repeat in range(0,lengte_scroll):
            self.__send_instruction(self.__instructScrollLeft)
            time.sleep(self.__scrollDelay)


    def __write_tekst(self, message, lengte):
        print(f"WRITE {message} to LCD")
        for index in range(0,lengte):
            self.__write_char(message[index])
    

    def __write_char(self, character):
        char = ord(character)
        self.__send_character(char)


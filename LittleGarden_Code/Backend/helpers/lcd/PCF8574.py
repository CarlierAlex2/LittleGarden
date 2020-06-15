from RPi import GPIO
import time

class PCF8574:
    def __init__(self, sda_pin, scl_pin, address, delay = 0.002, reversedPins=False):

        self.sda_pin = sda_pin
        self.scl_pin = scl_pin
        self.reversed_pins = reversedPins

        self.delay = delay
        self.schrijf_bit = 0
        self._address = address
        #print(f"Address is : {self._address}")


        GPIO.setup(self.sda_pin, GPIO.OUT)
        GPIO.setup(self.scl_pin, GPIO.OUT)


    @property
    def dot(self):
        return self._dot

    @dot.setter
    def dot(self, value: bool):
        self._dot = value

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        self._address = value


    def __send_SDA(self, send_waarde):
        self.__send_pin(self.sda_pin, send_waarde)


    def __send_SCL(self, send_waarde):
        self.__send_pin(self.scl_pin, send_waarde)


    def __send_pin(self, pin, send_waarde):
        GPIO.output(pin, send_waarde)
        time.sleep(self.delay)



    def __start_conditie(self):
        self.__send_SDA(GPIO.HIGH)
        self.__send_SCL(GPIO.HIGH)

        self.__send_SDA(GPIO.LOW)
        self.__send_SCL(GPIO.LOW)


    def __stop_conditie(self):
        self.__send_SDA(GPIO.LOW)
        self.__send_SCL(GPIO.LOW)

        self.__send_SCL(GPIO.HIGH)
        self.__send_SDA(GPIO.HIGH)


    def __klok_puls(self):
        self.__send_SCL(GPIO.HIGH)  #lees in
        self.__send_SCL(GPIO.LOW) #stop met lezen


    def __write_bit(self, bitwaarde):
        self.__send_SDA(bitwaarde) #zet data klaar
        self.__klok_puls()


    def __write_byte(self, bytewaarde):
        debugString = ""
        #print(f"Byte to write {bin(bytewaarde)}")
        mask = int(0b10000000)
        if (self.reversed_pins == True):
            mask = int(0b00000001)

        for index in range(0,8):
            #print(f"Byte to write {bin(bytewaarde)} & {bin(mask)}")
            if (mask & bytewaarde):
                self.__write_bit(True)
                debugString += "1"
            else:
                self.__write_bit(False)
                debugString += "0"

            if (self.reversed_pins == True):
                mask = mask << 1
            else:
                mask = mask >> 1
        #print(f"Send byte - {debugString}")


    def __ack(self):
        GPIO.setup(self.sda_pin, GPIO.IN, GPIO.PUD_UP)
        time.sleep(self.delay)

        self.__send_SCL(GPIO.HIGH) #lees in

        status = GPIO.input(self.sda_pin)
        #if(status == GPIO.LOW):
        #    print("ACK OK")
        #else:
        #    print("ACK verkeerd!")

        GPIO.setup(self.sda_pin, GPIO.OUT)
        time.sleep(self.delay)

        self.__send_SCL(GPIO.LOW) #stop met lezen

        return status


    def __write_address_RW(self):
        #print(f"PCF - Addres: {self._address}")
        send = (self._address << 1) | self.schrijf_bit
        #print(f"PCF - AddresRW: {send}")
        self.__write_byte(send)
        self.__ack() #ACK


    def __write_data(self, data_byte):
        self.__write_byte(data_byte)
        self.__ack() #ACK



    def write_outputs(self, data: int):
        if data in range(0,256):
            #START
            #---------------------------------------
            self.__start_conditie()
            #print("PCF START")

            #ADRES +R/W
            #---------------------------------------
            #print("PCF RW")
            self.__write_address_RW()

            #DATA
            #---------------------------------------
            #print(f"PCF DATA - {data}")
            self.__write_data(data)

            #STOP
            #---------------------------------------
            self.__stop_conditie()
            #print("PCF STOP")
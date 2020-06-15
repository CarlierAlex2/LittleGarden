from RPi import GPIO
import time

class DHT11:
    def __init__(self, DHT11_pin):

        self.DHT11_pin = DHT11_pin

        self.humidity = 0
        self.temperature = 0

        self.error_DHT = False  # voor de checksum

        self.data_count = 43
        self.data_count_found = 0
        self.data = [0] * self.data_count
        self.result_bytes = [0] * 5

    # Gebruikersgemak functies
    #--------------------------------------------------------------------
    def delaySeconds(self, seconds):
        time.sleep(seconds)

    def pin_DHT11_as_output(self):
        GPIO.setup(self.DHT11_pin, GPIO.OUT)

    def pin_DHT11_as_input(self):
        GPIO.setup(self.DHT11_pin, GPIO.IN, GPIO.PUD_UP)

    def set_DHT11_output(self, waarde):
        GPIO.output(self.DHT11_pin, waarde)

    def read_DHT11_output(self):
        return GPIO.input(self.DHT11_pin)

    def reset_values(self):
        self.humidity = 0
        self.temperature = 0
        self.error_DHT = False 
        self.data = [0] * self.data_count
        self.result_bytes = [0] * 5
        self.data_count_found = 0


    # Gebruikersgemak functies
    #--------------------------------------------------------------------
    def start_DHT11(self):
        self.pin_DHT11_as_output()

        self.set_DHT11_output(GPIO.HIGH)
        self.delaySeconds(0.05)

        self.set_DHT11_output(GPIO.LOW)
        self.delaySeconds(0.02)

        self.set_DHT11_output(GPIO.HIGH)
        self.pin_DHT11_as_input()

    def read_bits_DHT11(self):
        last_time = time.time()
        current_time = last_time
        can_DHT = True
        count = 0


        while count < self.data_count and (current_time - last_time) < 0.1:
            current_time = time.time()
            is_high = self.read_DHT11_output()

            if is_high == 0 and can_DHT == True: #If DHT pin is low, go to next Dataset
                can_DHT = False
                current_time = time.time()
                self.data[count]=(current_time - last_time) #duration tells if bit = 0 or 1
                count += 1
                last_time=time.time()

            if is_high == 1:
                can_DHT = True

        #print(f" count {count}")
        self.data_count_found = count

    def time_to_bits(self):
        for i in range(0, 40):
            index = i + 3
            #print(f"{self.data[index]} us")
            if self.data[index] <= 0.0001: # 26us - 28 => 0    en  70 = 1
                self.data[index] = 0
            else:
                self.data[index] = 1


    def bits_to_bytes(self):
        for byte_count in range(0, 5): #5 bytes gestuurd

            byte = 0
            for index in range(0, 8): #8 bits naar byte
                if index < 7:
                    byte = byte << 1

                bit = int(self.data[index + byte_count * 8 + 3])
                byte = byte | bit

            self.result_bytes[byte_count] = byte

    def check_sum(self):
        #for i in range(0, 5):
            #waarde = self.result_bytes[i]
            #print(f"hex {hex(waarde)} - bin {bin(waarde)} - int {int(waarde)}")

        sum_bytes = self.result_bytes[0] + self.result_bytes[1] + self.result_bytes[2] + self.result_bytes[3]
        sum_bytes = sum_bytes & 255
        check_sum = self.result_bytes[4]

        #print(" ")
        #print("Sum - check")
        #print(f"{sum_bytes} - {check_sum}")
        if sum_bytes == check_sum and self.data_count_found > 0:
            self.error_DHT = False
            self.humidity = int(self.result_bytes[0]) + int(self.result_bytes[1]) / 100
            self.temperature = int(self.result_bytes[2]) + int(self.result_bytes[3]) / 100
        else:
            self.error_DHT = True


    # Publieke functies
    #--------------------------------------------------------------------
    def read_humidity_and_temp(self):
        self.start_DHT11()
        #print("read_bits_DHT11")
        self.read_bits_DHT11()
        #print("time_to_bits")
        self.time_to_bits()
        #print("bits_to_bytes")
        self.bits_to_bytes()
        #print("check_sum")
        self.check_sum()

        waardes = None
        if self.error_DHT == False:
            waardes = [self.humidity, self.temperature]

        self.reset_values()
        return waardes

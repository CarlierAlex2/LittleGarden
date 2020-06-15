from .BH1750.BH1750 import BH1750
from .DHT11.DHT11 import DHT11
from .soil_sensor.Mcp import Mcp
from .soil_sensor.Soil_Sensor import Soil_Sensor

from datetime import datetime
import time

from flask import jsonify

class MeasureHelper:
    def __init__(self, dht11_pin, grond_sensor_channel = 0):
        bh1750 = BH1750()
        dht11 = DHT11(dht11_pin)
        mcp = Mcp()
        soil_sensor = Soil_Sensor(grond_sensor_channel, mcp)

        self.bh1750 = bh1750
        self.dht11 = dht11
        self.soil_sensor = soil_sensor


    # ---------------------------------------------------------------------------------------------------------------------------------------------------
    def read_light(self):
        commentaar = "No measurement taken"
        licht_json = {"type" : "light", "waarde" : 0, "commentaar" : commentaar}
        #return licht_json

        try:
            light_value = None
            for i in range(0,100):
                if(light_value is None):
                    light_value = self.bh1750.read_light()
                if(light_value is not None and light_value is not 0):
                    break
                time.sleep(0.1)

            commentaar = ""
            if(light_value is None):
                commentaar = "Error: No measurement was available"
                light_value = 0

            print(f"Licht waarde = {light_value} lux")
            licht_json = {"type" : "light", "waarde" : light_value, "commentaar" : commentaar}
            return licht_json
        except ValueError:
            print("ERROR: NO measurement taken")

        commentaar = "ERROR: NO measurement taken"
        licht_json = {"type" : "light", "waarde" : 0, "commentaar" : commentaar}
        return licht_json




    def read_humidity_temp(self):
        humid_json = {"type" : "humid", "waarde" : 0, "commentaar" : "No measurement taken"}
        temp_json = {"type" : "temp", "waarde" : 0, "commentaar" : "No measurement taken"}
        dht11_json = [humid_json, temp_json]
        #return dht11_json

        try:
            light_value = None
            dht11_waardes = None
            for i in range(0,100):
                if(dht11_waardes is None):
                    dht11_waardes = self.dht11.read_humidity_and_temp()
                if(dht11_waardes is not None):
                    break
                time.sleep(0.1)

            commentaar = "Error: No measurement was available"
            humid_json = {"type" : "humid", "waarde" : 0, "commentaar" : commentaar}
            temp_json = {"type" : "temp", "waarde" : 0, "commentaar" : commentaar}
        
            if dht11_waardes is not None:
                humid_value = dht11_waardes[0]
                commentaar = ""
                print(f"Humid waarde = {humid_value} %")
                humid_json = {"type" : "humid", "waarde" : humid_value, "commentaar" : commentaar}


                temp_value = dht11_waardes[1]
                commentaar = ""
                print(f"Temp waarde = {temp_value} *C")
                temp_json = {"type" : "temp", "waarde" : temp_value, "commentaar" : commentaar}


            dht11_json = [humid_json, temp_json]
            return dht11_json
        except ValueError:
            print("ERROR: NO measurement taken")

        commentaar = "ERROR: NO measurement taken"
        humid_json = {"type" : "humid", "waarde" : 0, "commentaar" : commentaar}
        temp_json = {"type" : "temp", "waarde" : 0, "commentaar" : commentaar}
        dht11_json = [humid_json, temp_json]
        return dht11_json






    def read_water(self):
        commentaar = "Error: No measurement was available"
        water_json =  {"type" : "water", "waarde" : 0, "commentaar" : commentaar}
        #return water_json

        try:
            water_value = None
            count = 0
            for i in range(0,100):
                if(water_value is None):
                    water_value = self.soil_sensor.read_soilwater_percentage()
                    count += 1
                    if(count < 3):
                        water_value = None
                if(water_value is not None and water_value is not 0):
                    break
                time.sleep(0.1)

            commentaar = ""
            if(water_value is None):
                commentaar = "ERROR: NO measurement taken"
                water_value = 0

            print(f"Water waarde = {water_value} ")
            water_json = {"type" : "water", "waarde" : water_value, "commentaar" : commentaar}
            return water_json
        except ValueError:
            print("ERROR: NO measurement taken")

        commentaar = "ERROR: NO measurement taken"
        water_json =  {"type" : "water", "waarde" : 0, "commentaar" : commentaar}
        return water_json




    def read_sensor(self, measureType):
        if(measureType == "water"):
            return self.read_water()
        if(measureType == "light"):
            return self.read_light()
        if(measureType == "humid"):
            measure = self.read_humidity_temp()
            return measure[0]
        if(measureType == "temp"):
            measure = self.read_humidity_temp()
            return measure[1]


    def create_meting_json(self):
        now = datetime.now()
        datum = str(now.strftime("%d/%m/%Y %H:%M:%S"))

        time.sleep(1)
        water_json = self.read_water()


        time.sleep(1)
        licht_json = self.read_light()


        time.sleep(1)
        dht11_json = self.read_humidity_temp()
        humid_json = dht11_json[0]
        temp_json = dht11_json[1]



        metingen = []
        metingen.append(water_json)
        metingen.append(licht_json)
        metingen.append(humid_json)
        metingen.append(temp_json)


        jsonMeting = {"measurements" : metingen, "date" : datum}
        return jsonMeting
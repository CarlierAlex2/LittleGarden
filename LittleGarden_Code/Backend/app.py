# pylint: skip-file
from repositories.DataRepository import DataRepository
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS

from helpers.sensors.MeasureHelper import MeasureHelper
from helpers.devices_id.DeviceHelper import DeviceHelper
from helpers.lcd.IPaddressHelper import IPaddressHelper
from helpers.lcd.LCD_PCF import LCD_PCF
from helpers.ActionHelper import ActionHelper

from datetime import datetime, timedelta

import time
import threading

from RPi import GPIO

# Code voor setup hardware
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

measureHelper = MeasureHelper(19)
last_water_value = 0
last_light_value = 0

ipHelper = IPaddressHelper()
actionHelper = ActionHelper(21, 20)

SDA = 27
SCL = 22
E = 6
RS = 5
address = 56
lcd = LCD_PCF(SDA, SCL, E, RS, address, False, False)
lcd.displayOn = True
lcd.cursorOn = False
lcd.cursorBlink = False
lcd.init_LCD()


# Code voor setup backend en frontend
endpoint = '/api/v1'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Hier mag je om het even wat schrijven, zolang het maar geheim blijft en een string is'

socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)


# API ENDPOINTS
# ---------------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/')
def hallo():
    return "Server is running, er zijn momenteel geen API endpoints beschikbaar."

#region METHODS
#**********************************************************************************************************************************************************
def get_dict_eenheden():
    id_devices = DeviceHelper.get_ids_sensors()
    dict_units = {}
    for id in id_devices:
        device = get_device_by_id(id)
        unit = device["eenheid"]
        dict_units[id] = unit

    return dict_units


@app.route(endpoint + '/ip', methods=['GET'])
def get_ip_address():
    if request.method == 'GET':
        print('REQUEST ip address')

        ip_array = ipHelper.get_ip_address()

        if ip_array is not None:
            return jsonify(ip_array=ip_array), 200
        else:
            print("ERROR: No ips send to frontend")
            return jsonify("ERROR: No ips send to frontend"), 404


@app.route(endpoint + '/date', methods=['GET'])
def route_setup_period():
    if request.method == 'GET':
        print('REQUEST period dates')
        dates = get_default_period()

        if dates is not None:
            return jsonify(dates=dates), 200
        else:
            print("ERROR: GET period failed")
            return jsonify("ERROR: GET period failed"), 404

def get_default_period():
    now = datetime.today()
    nowDate = str(now.strftime("%Y-%m-%d"))
    timestamp = str(now.strftime("%H:%M:%S"))

    yesterday = now - timedelta(days=1)
    yesterday = str(yesterday.strftime("%Y-%m-%d"))

    dates = {
        "dateStart" : yesterday, 
        "timeStart" : timestamp, 
        "dateEnd" : nowDate, 
        "timeEnd" : timestamp
    }
    return dates
#endregion    



#region Devices
#**********************************************************************************************************************************************************
def get_device_by_id(id):
    response = DataRepository.read_device_by_id(id)
    return response

@app.route(endpoint + '/devices/type/<measureType>', methods=['GET'])
def get_devices_by_type(type):
    if request.method == 'GET':
        print('GET Device by type')
        response = DataRepository.read_device_by_type(measureType)
        return jsonify(devices=response), 200
#endregion    



#region MEASUREMENTS
#**********************************************************************************************************************************************************
#region MEASUREMENTS_JSON
#-------------------------------------------------------------------------------------
def get_measure_json_latest(measureType):
    deviceId = DeviceHelper.get_sensor_for_measureType(measureType)
    #print(f"get_measure_json_latest - {deviceId}")
    response = DataRepository.read_metingen_last_by_device(deviceId)

    measurement = None
    if response is not None:
        value = response["waarde"]
        comment = response["commentaar"]
        date = str(response["datum"])
        average = response["gemiddelde"]

        device = get_device_by_id(deviceId)
        unit = device["eenheid"]
        measurement = {"measureType" : measureType, "value" : value,"comment" : comment,"date" : date, "average" : average, "unit" : unit}
    else:
        print(f"No measure to json - type: {measureType}")
    return measurement


def get_measure_json_list(measureType, periodStart = None, periodEnd = None):
    deviceId = DeviceHelper.get_sensor_for_measureType(measureType)
    dict_units = get_dict_eenheden()

    if periodStart is None or periodEnd is None:
        json_period = get_default_period()
        dateStart = json_period["dateStart"]
        timeStart = json_period["timeStart"]
        periodStart = f"{dateStart} {timeStart}"

        dateEnd = json_period["dateEnd"]
        timeEnd = json_period["timeEnd"]
        periodEnd = f"{dateEnd} {timeEnd}"


    print(f"{periodStart} - {periodEnd}")
    periodStart_datetime = datetime.strptime(str(periodStart), "%Y-%m-%d %H:%M:%S")
    periodStart = periodStart_datetime.strftime("%Y-%m-%d %H:%M")
    #"%Y-%m-%d %H:%M"
    periodEnd_datetime = datetime.strptime(str(periodEnd), "%Y-%m-%d %H:%M:%S")
    periodEnd = periodEnd_datetime.strftime("%Y-%m-%d %H:%M")


    dates = DataRepository.read_dates_in_period(periodStart, periodEnd)
    print(f"from till {periodStart} - {periodEnd} => {len(dates)} dates found")
    print(f" ")
    hasMoreDays = False
    if (periodEnd_datetime - periodStart_datetime).days > 1:
        hasMoreDays = True

    measurement_list = []
    if dates is not None:
        for dates_obj in dates:
            date = dates_obj["datum_distinct"]
            #print(date)
            response = DataRepository.read_metingen_by_date_and_device(date, deviceId)
            if response is not None:
                date_string = str(date)

                measurement_arr = []
                for response_obj in response:
                    timestamp = str(response_obj["datum"])
                    timestamp_datetime = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    timestamp_string = str(timestamp_datetime.strftime("%H:%M"))
                    label = str(timestamp_datetime.strftime("%d/%m %H:%M"))
                    if hasMoreDays == False:
                        label = str(timestamp_datetime.strftime("%H:%M"))
                        label += "h"
                            
                        

                    measurement = {
                        "measureType" : measureType, 
                        "value" : response_obj["waarde"], 
                        "comment" : response_obj["commentaar"], 
                        "timestamp" : timestamp_string, 
                        "label" : label,
                        "unit" : dict_units[deviceId]
                    }
                    measurement_arr.append(measurement)

                if len(measurement_arr) > 0:
                    list_obj = {"day": date, "measurements": measurement_arr, "measureType" : measureType}
                    measurement_list.append(list_obj)

    if len(measurement_list) == 0:
        return measurement_list, 1
    elif measurement_list is not None and len(measurement_list) > 0:
        return measurement_list, 0
    return print('ERROR: return a list of measurements FAILED'), 2
#endregion    



@app.route(endpoint + '/measurements/latest', methods=['GET'])
def route_measurements_latest_list():
    if request.method == 'GET':
        print("")
        print('REQUEST last measurement')
        types = DeviceHelper.get_type_sensors()

        json_list = {}
        ERROR = None
        for measureType in types:
            measurement = get_measure_json_latest(measureType)
            if measurement is not None:
                json_list[measureType] = measurement
                print(f"get {measureType} - SUCCESS")
            else:
                ERROR = jsonify(f"ERROR: Get latest {measureType} failed")
                print(f"get {measureType} - FAILED")

        
        if ERROR is None:
            return jsonify(measurements=json_list), 200
        else:
            return ERROR, 404


@app.route(endpoint + '/measurements/period/<measureType>', methods=['PUT'])
def get_measurements_period(measureType):
    if request.method == 'PUT':
        print("")
        print('REQUEST period measurements')

        periodStart = None
        periodEnd = None
        try:
            period_data = DataRepository.json_or_formdata(request)
            start = period_data["periodStart"]
            periodStart = str(datetime.strptime(start, "%Y-%m-%d %H:%M:%S"))
            end = period_data["periodEnd"]
            periodEnd = str(datetime.strptime(end, "%Y-%m-%d %H:%M:%S"))
            print(f'{periodStart} - {periodEnd}')
        except:
            print("No valid dates given") 

        measurent_list, message = get_measure_json_list(measureType, periodStart, periodEnd)
        if message == 0 or message == 1:
            return jsonify(measurements=measurent_list), 200
        else:
            return jsonify("ERROR: Get period measurements FAILED"), 404


@app.route(endpoint + '/measurements', methods=['POST'])
def route_create_measurement():
    print("")
    print("CREATE measurements")
    if request.method == 'POST':
        result = create_measurement()
        if result == 0:
            return jsonify(status="CREATE measure SUCCES"), 201
        else:
            return jsonify(status="CREATE measure FAILED"), 404

def create_measurement():
    result = take_measurements()
    if result == 0:
        global last_water_value
        global last_light_value
        toggle_actuator("water", last_water_value)
        toggle_actuator("light", last_light_value)
    return result

def take_measurements():
    json_metingen = measureHelper.create_meting_json()

    date_string = json_metingen["date"]
    date = datetime.strptime(date_string, '%d/%m/%Y %H:%M:%S')
    measurement_list = json_metingen["measurements"]

    failCount = 0
    for measurement in measurement_list:
        result = add_measurement(measurement, date)
        if result == False:
            failCount += 1

    return failCount


def add_measurement(json, date):
    waarde = json["waarde"]
    comment = json["commentaar"]
    measureType = json["type"]

    deviceId = DeviceHelper.get_sensor_for_measureType(measureType)
    nieuwId = DataRepository.create_meting(deviceId, waarde, comment, date)
    print("")
    print(f"Sensor measure")
    print(f"-deviceId: {deviceId} - {measureType}")
    print(f"-value: {waarde}")
    print(f"-comment: {comment}")
    print(f"-date: {date}")
    print(f"-result - data ID - {nieuwId}")

    print("")
    print(f'DATABASE')
    if nieuwId is not None:
        if measureType == "water":
            global last_water_value
            last_water_value = waarde
        if measureType == "light":
            global last_light_value
            last_light_value = waarde
        print(f'- NEW {measureType} measurement-sensor success')
        print("")
        return True
    else:
        print(f'- NEW {measureType} measurement-sensor failed')
        print("")
        return False
#endregion      



#region Settings
#**********************************************************************************************************************************************************
@app.route(endpoint + '/settings/<measureType>', methods=['GET','PUT'])
def route_settings(measureType):
    if request.method == 'GET':
        return get_response_settings(measureType)

    if request.method == 'PUT':
        data = DataRepository.json_or_formdata(request)
        return put_settings(measureType, data)

def get_response_settings(measureType):
    json = get_settings(measureType)
    if json is not None:
        return jsonify(settings=json), 200
    else:
        return ERROR, 404

def get_settings(measureType):
    deviceId = DeviceHelper.get_sensor_for_measureType(measureType)
    print(f"Request settings - {measureType} - {deviceId}")

    settingMax = DataRepository.read_setting_max_by_deviceId(deviceId)
    settingMin = DataRepository.read_setting_min_by_deviceId(deviceId)
    device = DataRepository.read_device_by_id(deviceId)
    unit = device["eenheid"]

    json = {"measureType" : measureType, "unit" : unit}
    if settingMax is not None:
        json["settingMax"] = settingMax["waarde"]
    if settingMin is not None:
        json["settingMin"] = settingMin["waarde"]

    if settingMin is not None and settingMax is not None:
        return json
    else:
        return None

def put_settings(measureType, data):
    print(f'Put setting for {measureType}')
    deviceId = DeviceHelper.get_sensor_for_measureType(measureType)
    settingType = data["settingType"]
    settingValue = data["value"]
    response = DataRepository.update_settings_by_deviceId(deviceId, settingType, settingValue)
    if response is not None:
        return jsonify(status="update settings success", row_count=data), 201
    else:
        return jsonify(status="update settings failed", row_count=data), 404
#endregion



#region SOCKET IO
#**********************************************************************************************************************************************************
@socketio.on('connect')
def initial_connection():
    print('A new client connect')
    socketio.emit('B2F_update_page', {'status': "UPDATE page"})
    #measureHelper.create_meting_json()

@socketio.on("F2B_get_actuator")
def socket_get_actuator(json):
    print('Correct actuator UI')
    isPumpActive = 0
    if actionHelper.is_actuator_active("water"):
        isPumpActive = 1
    socketio.emit('B2F_actuator_toggled', {'measureType': "water", "status" : isPumpActive})

    isLedActive = 0
    if actionHelper.is_actuator_active("light"):
        isLedActive = 1
    socketio.emit('B2F_actuator_toggled', {'measureType': "light", "status" : isLedActive})


@socketio.on("F2B_toggle_actuator")
def socket_toggle_actuator(json):
    measureType = json['measureType']
    value = measureHelper.read_sensor(measureType)["waarde"]
    toggle_actuator(measureType, value, True)


def toggle_actuator(measureType, value, isForced = False):
    #get settings
    settings = get_settings(measureType)
    if settings is None: #stop if no settings were given
        return

    settingMax = settings["settingMax"]
    settingMin = settings["settingMin"]
    print("")
    print(f"SETTINGS - {measureType} COMPARE value {value} with range {settingMin} - {settingMax}")

    if value >= settingMax:
        print(f"{measureType} MAXIMUM REACHED")
        toggled = set_actuator(measureType, 0)
        #-----------------------------------------------------------------------------
    elif value <  settingMin:
        print(f"{measureType} BELOW MINIMUM")
        toggled = set_actuator(measureType, 1)
        isActive = actionHelper.is_actuator_active(measureType)
        if isActive == True: #if actuator is active, start monitor loop
            sensordId = DeviceHelper.get_sensor_for_measureType(measureType)
            threading.Timer(1, monitor_active_actuator, args=(measureType,sensordId)).start()
        #-----------------------------------------------------------------------------
    elif isForced == True and value >=  settingMin and value < settingMax:
        status = actionHelper.is_actuator_active(measureType)
        status = not status
        print(f"toggle_actuator - {status}")
        comment = f"manual"
        toggled = set_actuator(measureType, status, comment)
        isActive = actionHelper.is_actuator_active(measureType)
        if isActive == True: #if actuator is active, start monitor loop
            sensordId = DeviceHelper.get_sensor_for_measureType(measureType)
            threading.Timer(1, monitor_active_actuator, args=(measureType,sensordId)).start()


def set_actuator(measureType, status, message = "automatic"):
    print(f"set_actuator - {status}")
    if measureType is not None and status is not None:
        status = actionHelper.set_active(measureType, status)
        now = datetime.now()
        date = str(now.strftime("%Y-%m-%d %H:%M:%S"))
        comment = message
        deviceId = DeviceHelper.get_actuator_for_measureType(measureType)
        #print(f"Actuator measure - device ID - {device6Id}")
        isActive = 0
        if(status == True):
            isActive = 1

        nieuwId = DataRepository.create_meting(deviceId, isActive, comment, date)
        print("")
        print(f"Actuator measure")
        print(f"-deviceId: {deviceId} - {measureType}")
        print(f"-isActive: {isActive}")
        print(f"-comment: {comment}")
        print(f"-date: {date}")
        print(f"-result - data ID - {nieuwId}")

        print("")
        print(f'DATABASE')
        if nieuwId is not None:
            print(f"- NEW {measureType} measurement-actuator success")
            print("")
            socketio.emit('B2F_actuator_toggled', {'measureType': measureType, "status" : isActive})
            return True
        else:
            print(f"- NEW {measureType} measurement-actuator failed")
            print("")
            actionHelper.set_active(measureType, False)
            return False
    else:
        print("")
        print('ERROR: Toggle FAILED <==')
        print("")
        return False
#endregion



#region THREAD
#**********************************************************************************************************************************************************
time_between_meting = 10 * 60 #10 minuten
def maak_metingen():
    print("")
    print("Start automatic measurements")
    print("")
    create_measurement()
    socketio.emit('B2F_update_page', {'status': "UPDATE page"}, broadcast=True)
    threading.Timer(time_between_meting, maak_metingen).start()


def setup_actuators():
    set_actuator("water", 0)
    set_actuator("light", 0)


def print_ip():
    ip_array = ipHelper.get_ip_address()
    for message in ip_array:
        lcd.clear_LCD()
        print(f"PRINT IP address - {message}")
        lcd.write_message(message)
        time.sleep(15)
    threading.Timer(1, print_ip).start()


def monitor_active_actuator(measureType, sensordId):
    #update current value and maximum value
    print(f"ACTUATOR - {measureType} monitor")
    setting = DataRepository.read_setting_max_by_deviceId(sensordId)
    if setting is None:
        comment = f"NO SETTINGS FOUND FOR ACTUATOR - TURN OFF"
        print(comment)
        set_actuator(measureType, 0, comment)
        return

    settingMax = setting["waarde"]
    value = measureHelper.read_sensor(measureType)["waarde"]
    comment = "automatic"

    #stop thread if actuator is deactivated
    if actionHelper.is_actuator_active(measureType) == False:
        print(f"ACTUATOR - {measureType} turned OFF MANUALLY")
        set_actuator(measureType, 0, comment)
        return
        
   #check for improvement
    if value < settingMax:  #if no improvement, wait
        threading.Timer(10, monitor_active_actuator, args=(measureType,sensordId)).start()
    else: #if improvement, stop actuator
        print(f"ACTUATOR - {measureType} turned OFF")
        set_actuator(measureType, 0, comment)



#endregion


# RUN APP
# ---------------------------------------------------------------------------------------------------------------------------------------------------
try:
    threading.Timer(1, print_ip).start()
    setup_actuators()
    maak_metingen()
    
    if __name__ == '__main__':
        socketio.run(app, debug=False, host='0.0.0.0')

    GPIO.cleanup()

except KeyboardInterrupt as e:
    GPIO.cleanup()
    print(e)

finally:
    GPIO.cleanup()
    print("finally")


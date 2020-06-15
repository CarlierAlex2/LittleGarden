
array_device_id = [5, 6]
array_device_type = ["water", "light"]

dict_devices = {}
dict_types = {}
for index in range(0, len(array_device_id)):
    dict_types[array_device_id[index]] = array_device_type[index]
    dict_devices[array_device_type[index]] = array_device_id[index]



class ActuatorHelper:
    @staticmethod
    def get_device_for_measureType(measureType):
        measureType = measureType.lower()
        devideId = 0

        if measureType in dict_devices:
            devideId = dict_devices[measureType]

        return devideId

    @staticmethod
    def get_measureType_for_device(deviceId):
        measureType = ""

        if deviceId in dict_types:
            measureType = dict_types[deviceId]

        
        return measureType

    @staticmethod
    def get_ids_devices():
        return array_device_id

    @staticmethod
    def get_type_devices():
        return array_device_type
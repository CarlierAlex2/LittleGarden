from .SensorHelper import SensorHelper
from .ActuatorHelper import ActuatorHelper

class DeviceHelper:
    @staticmethod
    def get_sensor_for_measureType(measureType):
        return SensorHelper.get_device_for_measureType(measureType)

    @staticmethod
    def get_actuator_for_measureType(measureType):
        return ActuatorHelper.get_device_for_measureType(measureType)



    @staticmethod
    def get_measureType_for_sensor(deviceId):
        return SensorHelper.get_measureType_for_device(deviceId)

    @staticmethod
    def get_measureType_for_actuator(deviceId):
        return ActuatorHelper.get_measureType_for_device(deviceId)



    @staticmethod
    def get_ids_sensors():
        return SensorHelper.get_ids_devices()

    @staticmethod
    def get_ids_actuators():
        return ActuatorHelper.get_ids_devices()



    @staticmethod
    def get_type_sensors():
        return SensorHelper.get_type_devices()

    @staticmethod
    def get_type_actuators():
        return ActuatorHelper.get_type_devices()
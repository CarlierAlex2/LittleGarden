from .Database import Database


class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens


# GET WHOLE TABLE
# ---------------------------------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def read_devices():
        sql = "SELECT naam, eenheid, typeDevice from Devices"
        return Database.get_rows(sql)

    @staticmethod
    def read_metingen():
        sql = "SELECT * from Metingen"
        return Database.get_rows(sql)

    @staticmethod
    def read_settings():
        sql = "SELECT * from Settings"
        return Database.get_rows(sql)


# GET BY ID
# ---------------------------------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def read_device_by_id(id):
        sql = "SELECT naam, eenheid, typeDevice from Devices WHERE deviceId = %s"
        params = [id]
        return Database.get_one_row(sql, params)

    @staticmethod
    def read_meting_by_id(id):
        sql = "SELECT * from Metingen WHERE metingId = %s"
        params = [id]
        return Database.get_one_row(sql, params)

    @staticmethod
    def read_setting_by_id(id):
        sql = "SELECT * from Settings WHERE settingId = %s"
        params = [id]
        return Database.get_one_row(sql, params)




# GET DEVICES
# ---------------------------------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def read_device_by_type(typeDevice):
        sql = "SELECT * from Devices WHERE typeDevice = %s"
        params = [typeDevice]
        return Database.get_rows(sql, params)  

    @staticmethod
    def read_actuators():
        return DataRepository.read_device_by_type("actuator")  

    @staticmethod
    def read_sensors(datum):
        return DataRepository.read_device_by_type("sensor")  

    @staticmethod
    def create_device(naam, merk, prijs, beschrijving, eenheid, typeDevice):
        sql = "INSERT INTO Devices(naam, merk, prijs, beschrijving, eenheid, typeDevice) waardeS(%s,%s,%s,%s,%s,%s)"
        params = [naam, merk, prijs, beschrijving, eenheid, typeDevice]
        return Database.execute_sql(sql, params)



# GET METINGEN
# ---------------------------------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def read_metingen_from_date(deviceId, datum):
        sql = "SELECT * from Metingen WHERE deviceId = %s datum = %s"
        params = [deviceId, datum]
        return Database.get_rows(sql, params)

    @staticmethod
    def read_metingen_last_by_device(deviceId):
        sql = "SELECT deviceId, waarde, commentaar, datum, AVG(waarde) OVER (PARTITION BY CAST(datum as date)) as gemiddelde FROM Metingen WHERE deviceId = %s ORDER BY datum desc;"
        params = [deviceId]
        return Database.get_one_row(sql, params)

    @staticmethod
    def read_metingen_from_moment(deviceId, time):
        sql = "SELECT * from Metingen WHERE deviceId = %s AND CAST(datum as time) = %s "
        params = [deviceId, time]
        return Database.get_rows(sql, params)

    @staticmethod
    def read_metingen_from_period_grouped(datumBegin, datumEind):
        #sql = "SELECT * from Metingen water WHERE CAST(datum as time) >= %s AND CAST(datum as time) < %s"
        sql = "SELECT datum,"
        sql += "max(case when deviceId = 1 then waarde else 0 end) as water,"
        sql += "max(case when deviceId = 2 then waarde else 0 end) as licht,"
        sql += "max(case when deviceId = 3 then waarde else 0 end) as humid,"
        sql += "max(case when deviceId = 4 then waarde else 0 end) as temp"
        sql += "FROM Metingen"
        sql += "WHERE datum >= %s AND datum <= %s"
        sql += "GROUP BY datum"
        sql += "ORDER BY datum desc "

        params = [datumBegin, datumEind]
        return Database.get_rows(sql, params)

    @staticmethod
    def read_metingen_by_period_and_device(datumBegin, datumEind, deviceId):
        #sql = "SELECT * from Metingen water WHERE CAST(datum as time) >= %s AND CAST(datum as time) < %s"
        sql = "SELECT datum, waarde, commentaar, deviceId "
        sql += "FROM Metingen "
        sql += "WHERE datum >= CAST(%s as datetime) AND datum <= CAST(%s as datetime) AND deviceId = %s "
        sql += "ORDER BY datum desc, deviceId "

        params = [datumBegin, datumEind, deviceId]
        return Database.get_rows(sql, params)

    @staticmethod
    def read_metingen_by_period(datumBegin, datumEind):
        #sql = "SELECT * from Metingen water WHERE CAST(datum as time) >= %s AND CAST(datum as time) < %s"
        sql = "SELECT datum, waarde, commentaar, deviceId "
        sql += "FROM Metingen "
        sql += "WHERE datum >= CAST(%s as datetime) AND datum <= CAST(%s as datetime) "
        sql += "ORDER BY datum desc, deviceId "

        params = [datumBegin, datumEind]
        return Database.get_rows(sql, params)

    @staticmethod
    def read_metingen_by_date_and_device(date, deviceId):
        #sql = "SELECT * from Metingen water WHERE CAST(datum as time) >= %s AND CAST(datum as time) < %s"
        sql = "SELECT datum, waarde, commentaar, deviceId "
        sql += "FROM Metingen "
        sql += "WHERE DATE_FORMAT(datum, '%Y-%m-%d') = %s AND deviceId = %s "
        sql += "ORDER BY datum desc, deviceId "

        params = [date, deviceId]
        return Database.get_rows(sql, params)

    @staticmethod
    def read_dates_in_period(datumBegin, datumEind):
        sql = "SELECT distinct(DATE_FORMAT(datum, '%Y-%m-%d')) as datum_distinct "
        sql += "FROM Metingen "
        sql += "WHERE datum >= CAST(%s as datetime) AND datum <= CAST(%s as datetime) "
        sql += "ORDER BY datum_distinct desc "

        params = [datumBegin, datumEind]
        return Database.get_rows(sql, params)

    @staticmethod
    def create_meting(deviceId, waarde, commentaar, datum):
        sql = "INSERT INTO Metingen(deviceId, waarde, commentaar, datum) VALUES(%s,%s,%s,%s) "
        params = [deviceId, waarde, commentaar, datum]
        return Database.execute_sql(sql, params)


# SETTINGS
# ---------------------------------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def read_settings_by_deviceId(deviceId):
        sql = "SELECT * from Settings WHERE deviceId = %s"
        params = [deviceId]
        return Database.get_rows(sql, params)

    @staticmethod
    def create_setting(deviceId, waarde, typeSetting):
        sql = "INSERT INTO Settings(deviceId, waarde, type) waardeS(%s,%s,%s)"
        params = [deviceId, waarde, typeSetting]
        return Database.execute_sql(sql, params)

    @staticmethod
    def update_settings_by_deviceId(deviceId, settingType, waarde):
        sql = "UPDATE Settings SET waarde = %s WHERE type  = %s and deviceId = %s "
        params = [waarde, settingType, deviceId]
        return Database.execute_sql(sql, params)

    @staticmethod
    def read_setting_max_by_deviceId(deviceId):
        sql = "SELECT deviceId, waarde, type from Settings WHERE type in ('top','max') and deviceId = %s"
        params = [deviceId]
        return Database.get_one_row(sql, params)

    @staticmethod
    def read_setting_min_by_deviceId(deviceId):
        sql = "SELECT deviceId, waarde, type from Settings WHERE type in ('bottom','min') and deviceId = %s"
        params = [deviceId]
        return Database.get_one_row(sql, params)

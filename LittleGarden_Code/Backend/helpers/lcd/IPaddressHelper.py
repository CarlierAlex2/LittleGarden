#IP
from subprocess import check_output

class IPaddressHelper:
    @staticmethod
    def get_ip_address():
        ips_waarde = check_output(['hostname', '--all-ip-addresses'])
        ips = str(ips_waarde)
        ips = ips.strip('b')
        ips = ips.strip('\'')
        ips = ips.split(" ")

        ip_string = ""
        aantal = len(ips)
        for index in range(0,aantal - 1):
            ip = ips[index]
            ip_string += f"{ip} "
        ip_string = ip_string.rstrip()
        ips = ip_string.split(" ")

        return ips
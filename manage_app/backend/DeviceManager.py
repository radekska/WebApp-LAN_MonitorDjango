from threading import Thread
from queue import Queue
from easysnmp import Session
from config_app.backend.helpers import get_thread_output
from manage_app.backend import parse_model, static


class DeviceManager:
    """
    This class is used to create multiple device objects by retrieving data via SNMP from all device in specified
    network.

    Constructor Positional Arguments:
    - user -- django User model object
    - available_hosts -- list of available IP addresses (network devices)
    - snmp_config_id -- id which referees to initially provided SNMP configuration

    """

    def __init__(self, user, available_hosts, snmp_config_id):
        self.user = user
        self.available_host = available_hosts
        self.snmp_config_id = snmp_config_id
        self.session_parameters = parse_model.parse_to_session_parameters(self.snmp_config_id)

    def __get_single_device_details(self, hostname):
        session = Session(hostname=hostname, **self.session_parameters)
        device = Device(hostname, session)
        return device

    def get_multiple_device_details(self):
        thread_list = list()
        session_queue = Queue()

        for host in self.available_host:
            session_thread = Thread(target=lambda in_que, args: in_que.put(self.__get_single_device_details(host)),
                                    args=(session_queue, host))
            session_thread.start()
            thread_list.append(session_thread)

        devices_details_output = get_thread_output(session_queue, thread_list)
        return devices_details_output


class DeviceSystem_:
    """
    This class uses easysnmp session object to retrieve all SNMP system MIB data.

    Constructor Positional Arguments:
    - hostname -- IP address of connected device
    - session -- easysnmp Session class instance
    """

    def __init__(self, hostname, session):
        self.system_description = session.get(('sysDescr', 0)).value
        self.system_contact = session.get(('sysContact', 0)).value
        self.full_system_name = session.get(('sysName', 0)).value
        self.system_location = session.get(('sysLocation', 0)).value
        self.system_up_time = session.get(('sysUpTime', 0)).value
        self.hostname = hostname


class DeviceInterface_:
    """
    This class uses easysnmp session object to retrieve all SNMP interface MIB data.

    Constructor Positional Arguments:
    - number -- interface number
    - session -- easysnmp Session class instance
    """

    def __init__(self, number, session):
        self.interface_idx = session.get(('ifName', number)).oid_index
        self.interface_name = session.get(('ifName', number)).value
        self.interface_description = session.get(('ifDescr', number)).value
        self.interface_type = session.get(('ifType', number)).value
        self.interface_mtu = session.get(('ifMtu', number)).value
        self.interface_speed = session.get(('ifSpeed', number)).value
        self.interface_physical_addr = session.get(('ifPhysAddress', number)).value
        self.interface_admin_status = session.get(('ifAdminStatus', number)).value
        self.interface_operational_status = session.get(('ifOperStatus', number)).value

        self.interface_in_unicast_packets = session.get(('ifInUcastPkts', number)).value
        self.interface_in_errors = session.get(('ifInErrors', number)).value
        self.interface_out_unicast_packets = session.get(('ifOutUcastPkts', number)).value
        self.interface_out_errors = session.get(('ifOutErrors', number)).value

        self.lldp_neighbor_name = None
        self.lldp_neighbor_interface = None

        self.interface_ip = None
        ip_addresses = session.walk('ipAdEntIfIndex')
        for snmp_query in ip_addresses:
            if snmp_query.value == self.interface_idx:
                self.interface_ip = snmp_query.oid_index


class Device:
    """
    This class both DeviceInterface_ and DeviceSystem_ classes to merge together all the data and create one final
    Device object with neighbor details as well.

    Constructor Positional Arguments:
    - hostname -- IP address of connected device
    - session -- easysnmp Session class instance
    """

    def __init__(self, hostname, session):
        self.hostname = hostname
        self.session = session
        self.system = DeviceSystem_(self.hostname, self.session)
        self.if_number = int(self.session.get(('ifNumber', 0)).value)
        self.interfaces = [DeviceInterface_(number, self.session) for number in range(1, self.if_number + 1)]
        self.lldp_data = self.__get_lldp_entries()

    def __get_lldp_entries(self):
        # THIS FUNCTION WORKS WRONG WHEN INT DESCRIPTIONS ARE ADDED - SOME BACKEND ISSUES WITH EASYSNMP WALK !!!
        lldp_remote_systems_data = self.session.walk(static.lldp_defined_values['lldpRemoteSystemsData'])

        lldp_remote_query = {
            'lldp_neighbor_interfaces': list(),
            'lldp_neighbor_hostnames': list(),
        }
        for item in lldp_remote_systems_data:
            if static.lldp_defined_values['lldpNeighborInterface'] in item.oid:
                lldp_remote_query['lldp_neighbor_interfaces'].append(item.value)
            elif static.lldp_defined_values['lldpNeighborHostName'] in item.oid:
                lldp_remote_query['lldp_neighbor_hostnames'].append(item.value)

        lldp_neighbor_correlation = zip(lldp_remote_query['lldp_neighbor_interfaces'],
                                        lldp_remote_query['lldp_neighbor_hostnames'])
        lldp_final_correlation = dict()

        for lldp_neighbor_interface, lldp_neigbor_hostname in lldp_neighbor_correlation:
            lldp_final_correlation[lldp_neigbor_hostname] = lldp_neighbor_interface

        lldp_final_query = {
            self.system.full_system_name: lldp_final_correlation
        }
        return lldp_final_query

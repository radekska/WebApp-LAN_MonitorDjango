import napalm
import threading
from config_app.backend import helpers
from queue import Queue


class ConfigManager:
    """
    This class connects to all devices specified in available_hosts list
    and configure them with given SNMP configuration.

    Constructor positional arguments:
    - initial_config_data -- dictionary with device parameters
    - login_params -- dictionary with access device details
    - available_hosts -- list of LAN available devices
    """

    def __init__(self, initial_config_data, login_params, available_hosts):
        self.initial_config_data = initial_config_data
        self.login_params = login_params
        self.available_hosts = available_hosts

    def __connect_and_change_single(self, host, config_commands, type_of_change='configure'):
        driver = napalm.get_network_driver(self.initial_config_data['system'].get('network_dev_os', 'ios'))
        connection = driver(hostname=host, **self.login_params['napalm'])
        message = None
        state = None
        try:
            connection.open()
        except Exception as exc:
            message = str(exc)
            state = 'error'
        else:
            if type_of_change == 'configure':
                connection.load_merge_candidate(config=config_commands)
                connection.commit_config()
                message = 'SNMPv3 Configuration Successful!'
                state = 'success'
            elif type_of_change == 'rollback':
                connection.rollback()
                message = 'SNMPv3 Configuration Removal Successful!'
                state = 'success'

        finally:
            return connection.hostname, message, state

    def connect_and_configure_multiple(self, config_commands=None, type_of_change='configure'):
        threads_list = list()
        connection_que = Queue()

        for host in self.available_hosts:
            connect_thread = threading.Thread(target=lambda in_que, args: in_que.put(
                self.__connect_and_change_single(host, config_commands, type_of_change)),
                                              args=(connection_que, [host, config_commands, type_of_change]))

            connect_thread.start()
            threads_list.append(connect_thread)

        conf_output = helpers.get_thread_output(connection_que, threads_list)
        return conf_output

    def get_command_output(self):
        driver = napalm.get_network_driver(self.initial_config_data['system'].get('network_dev_os', 'ios'))
        login_params = self.login_params['napalm']

        threads_list = list()
        connection_que = Queue()

        for host in self.available_hosts:
            device = driver(hostname=host, **login_params)
            connect_thread = threading.Thread(
                target=lambda in_que, args: in_que.put(helpers.connect_and_get_output(device)),
                args=(connection_que, device,))

            connect_thread.start()
            threads_list.append(connect_thread)

        command_output = helpers.get_thread_output(connection_que, threads_list)
        command_output = list(filter(lambda data: data is not None, command_output))
        return command_output

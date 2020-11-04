import logging

from easysnmp import Session
from datetime import datetime

from pysnmp.proto import api
from pyasn1.codec.ber import decoder
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.carrier.asyncore.dispatch import AsyncoreDispatcher

from manage_app.models import DeviceTrapModel, VarBindModel, DeviceInterface, DeviceModel


class TrapEngine:
    def __init__(self, snmp_host, snmp_host_port, session_parameters):
        self.snmp_host = snmp_host
        self.snmp_host_port = snmp_host_port
        self.session_parameters = session_parameters

        self.udp_domain_name = udp.domainName
        self.udp_socket_transport = udp.UdpSocketTransport

    def _receive_and_save(self, transportDispatcher, transportDomain, transportAddress, wholeMsg):

        while wholeMsg:

            msgVer = int(api.decodeMessageVersion(wholeMsg))
            if msgVer in api.protoModules:
                pMod = api.protoModules[msgVer]

            else:
                logging.warning('Unsupported SNMP version %s' % msgVer)
                return

            reqMsg, wholeMsg = decoder.decode(
                wholeMsg, asn1Spec=pMod.Message(),
            )

            logging.warning('########## RECEIVED NEW TRAP ########## ')
            logging.warning(f'Notification message from {transportDomain}:{transportAddress}')

            reqPDU = pMod.apiMessage.getPDU(reqMsg)

            if reqPDU.isSameTypeWith(pMod.TrapPDU()):
                trap_date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                trap_domain = transportDomain
                trap_address = transportAddress[0]
                trap_port = transportAddress[1]

                logging.warning(f'Datetime: {trap_date}')
                logging.warning(f'Trap Domain: {trap_domain}')
                logging.warning(f'Agent Address: {trap_address}:{trap_port}')

                full_system_name = self._get_system_name(trap_address)
                device_model = DeviceModel.objects.filter(full_system_name=full_system_name)[0]

                trap_model_parameters = {
                    'device_model': device_model,
                    'trap_domain': trap_domain,
                    'trap_address': trap_address,
                    'trap_port': trap_port,
                    'trap_date': trap_date
                }
                trap_model = DeviceTrapModel(**trap_model_parameters)
                trap_model.save()
                varBinds = pMod.apiTrapPDU.getVarBinds(reqPDU)

                for trap_oid, trap_data in varBinds:
                    var_bids_parameters = {
                        'trap_model': trap_model,
                        'trap_oid': trap_oid,
                        'trap_data': trap_data
                    }

                    var_bids_model = VarBindModel(**var_bids_parameters)
                    var_bids_model.save()

            else:
                varBinds = pMod.apiPDU.getVarBinds(reqPDU)

            logging.warning('Var-binds:')
            for oid, val in varBinds:
                logging.warning('%s = %s' % (oid, val))

        return wholeMsg

    def _get_system_name(self, trap_address):

        self.session_parameters['hostname'] = trap_address

        session = Session(**self.session_parameters)
        full_system_name = session.walk('sysName')[0].value

        return full_system_name

    def _initialize_engine(self):
        self.transport_dispatcher = AsyncoreDispatcher()
        self.transport_dispatcher.registerRecvCbFun(self._receive_and_save)
        self.transport_dispatcher.registerTransport(self.udp_domain_name,
                                                    self.udp_socket_transport().openServerMode(
                                                        (self.snmp_host, self.snmp_host_port)))

        self.transport_dispatcher.jobStarted(1)

    def run_engine(self):
        self._initialize_engine()
        self.transport_dispatcher.runDispatcher()

    def close_engine(self):
        self.transport_dispatcher.closeDispatcher()

import bluetooth

class RFCOMM:
    def __init__(self):
        self._server_sock=bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self._server_sock.bind(("",bluetooth.PORT_ANY))
        self._server_sock.listen(1)
        self._service_name = "RKZDAC"
        self._client_sock = None
        self._client_info = None
        self._port = self._server_sock.getsockname()[1]
        self._uuid = "985047f6-6099-4920-9781-4199d586103f"

        bluetooth.advertise_service( self._server_sock, self._service_name,
                    service_id = self._uuid,
                    service_classes = [self._uuid, bluetooth.SERIAL_PORT_CLASS],
                    profiles = [bluetooth.SERIAL_PORT_PROFILE])

    def wait_for_client(self):
        self._client_sock, self._client_info = self._server_sock.accept()


    def send_data(self, data):
        if self.client_connected:
            try:
                self._client_sock.send(data)
                return True
            except bluetooth.btcommon.BluetoothError as e:
                print("closing...")
                self.close()
                return False
        else:
            return False

    def close(self):
        self._client_sock = None

    @property
    def client_connected(self):
        return self._client_sock != None

    @property
    def service_name(self):
        return self._service_name

    @property
    def service_uuid(self):
        return self._uuid
# file: BluetoothServer.py
# auth: mininerej <chocom@tonkotsu-ra.men>
# TODO: desc: ~~~~~
from bluetooth import *
import logging
import iwlist


logging.basicConfig(level=logging.DEBUG)

WIFI_STATUS = 0
WIFI_LIST = 1
CONNECT_WIFI = 2


class BluetoothServer:
    def __init__(self):
        self.server_sock = BluetoothSocket(RFCOMM)
        self.server_sock.bind(("", PORT_ANY))
        self.server_sock.listen(1)

        port = self.server_sock.getsockname()[1]

        uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

        advertise_service(self.server_sock, "SampleServer",
                          service_id=uuid,
                          service_classes=[uuid, btcommon.SERIAL_PORT_CLASS],
                          profiles=[btcommon.SERIAL_PORT_PROFILE]
                          #                   protocols = [ OBEX_UUID ]
                          )

        print("Waiting for connection on RFCOMM channel %d" % port)

        self.client_sock, self.client_info = self.server_sock.accept()
        print("Accepted connection from ", self.client_info)

    def process_request(self, data):
        title = data['title']
        contents = data['contents']

        # Request for wifi connection status information
        if title == WIFI_STATUS:
            wifi_status_data = iwlist.check()
            self.server_sock.send(wifi_status_data)
            logging.info("wifi connection status data was sent!")
            self.server_sock.close()

        elif title == WIFI_LIST:
            scan_data = iwlist.scan()
            self.server_sock.send(scan_data)
            logging.info("iwlist data was sent!")
            self.server_sock.close()

        elif title == CONNECT_WIFI:
            SSID = contents["SSID"]
            PW = contents["PW"]
            result = iwlist.connect(SSID, PW)
            if len(result) == 0:
                self.server_sock.send(0)
                logging.info("wifi connected with SSID : ",SSID)
                self.server_sock.close()

            # TODO: if wifi connected start face recognition
            #  android should get face recognition state from server.

        else:
            logging.info("Wrong request")
            return

    def run(self):
        try:
            while True:
                data = self.client_sock.recv(1024)
                if len(data) == 0: break
                print("received [%s]" % data)
        except IOError:
            pass
        except KeyboardInterrupt as e:
            print("KeyboardInterrupt", e.args);


        print("disconnected")
        self.client_sock.close()
        self.server_sock.close()
        print("Server exit")

if __name__ == "__main__":
    server = BluetoothServer()
    logging.info("Server instance created!")
    server.run()

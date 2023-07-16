# NSCOM01 - S12
# Machine Project #1
# CORPUZ, John Exequiel A.
# DIAZ, Sebastian Q.

import socket
import struct

TFTP_PORT = 69
MAX_BLOCK_SIZE = 512
TIMEOUT = 5  # in seconds

OP_RRQ = 1  # Read request
OP_WRQ = 2  # Write request
OP_DATA = 3  # Data
OP_ACK = 4  # Acknowledgement
OP_ERROR = 5  # Error


def pack_request(opcode, filename, mode="octet"):
    return struct.pack('!H', opcode) + filename.encode() + b'\0' + mode.encode() + b'\0'


class TFTPSession:
    def __init__(self, server_ip):
        self.server_ip = server_ip
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.settimeout(TIMEOUT)

    def upload(self, local_name, remote_name):
        try:
            with open(local_name, "rb") as f:
                pass
        except FileNotFoundError:
            print("File not found. Please check if the file exists in the local directory.")
            return

        request = pack_request(OP_WRQ, remote_name)
        self.client.sendto(request, (self.server_ip, TFTP_PORT))

        try:
            response, addr = self.client.recvfrom(2048)
        except:
            print("Timeout error. Please check if the server is running or configured properly.")
            return

        opcode = response[1]

        if opcode == OP_ERROR:
            error_message = response[4:].decode()
            print(f"Error from server: {error_message}")
        else:
            with open(local_name, "rb") as f:
                block_number = 0
                while True:
                    data = f.read(MAX_BLOCK_SIZE)
                    block_number += 1

                    packet = bytearray([0, OP_DATA, 0, block_number]) + data
                    self.client.sendto(packet, addr)

                    try:
                        ack_response, ack_addr = self.client.recvfrom(2048)
                        ack_opcode = ack_response[1]
                        ack_block_number = struct.unpack('!H', ack_response[2:4])[0]

                        if ack_opcode == OP_ERROR:
                            print(f"Error from server: {ack_response[4:].decode()}")
                            break
                        elif ack_opcode == OP_ACK and ack_block_number == block_number:
                            if len(data) < MAX_BLOCK_SIZE:
                                break
                        else:
                            print("Unexpected response from the server.")
                            break

                    except socket.timeout:
                        print("Timeout error. Please try again.")
                        return

                    except:
                        print("Unexpected error. Please try again.")
                        return

            print(f"Uploaded {local_name} to server as {remote_name}.")

    def download(self, remote_name, local_name):
        request = pack_request(OP_RRQ, remote_name)
        self.client.sendto(request, (self.server_ip, TFTP_PORT))

        try:
            response, addr = self.client.recvfrom(2048)
        except:
            print("Timeout error. Please check if the server is running or configured properly.")
            return

        opcode = response[1]

        if opcode == OP_ERROR:
            error_message = response[4:].decode()
            print(f"Error from server: {error_message}")
        else:
            try:
                with open(local_name, "wb") as f:
                    block_number = 1
                    while True:
                        opcode = response[1]
                        if opcode == OP_DATA:
                            received_block_number = struct.unpack('!H', response[2:4])[0]
                            data = response[4:]

                            if received_block_number == block_number:
                                f.write(data)

                                ack = bytearray([0, OP_ACK, 0, block_number])
                                self.client.sendto(ack, addr)

                                block_number += 1

                            if len(data) < MAX_BLOCK_SIZE:
                                break

                        elif opcode == OP_ERROR:
                            print(f"Error from server: {response[4:].decode()}")
                            break

                        response, addr = self.client.recvfrom(2048)

                    print(f"Saved {remote_name} from server as {local_name}.")
            except FileNotFoundError:
                print("Error saving file. Please check if the file path is valid.")
                return
            except:
                print("Unexpected error. Please try again.")
                return

def main():
    print("Simple TFTP Client")
    print("Before anything, please make sure that your TFTP server is running and configured properly.")
    print("We recommend using TFTPD64 because this client was only tested with that software.")
    server_ip = input("Enter TFTP server IP address: ")
    session = TFTPSession(server_ip)

    while True:
        action = input("Enter action (upload/download/exit): ")
        if action == "upload":
            local_name = input("Enter local file path: ")
            remote_name = input("Enter remote file name: ")
            session.upload(local_name, remote_name)
        elif action == "download":
            remote_name = input("Enter remote file name: ")
            local_name = input("Enter local file path: ")
            session.download(remote_name, local_name)
        elif action == "exit":
            break
        else:
            print("Invalid action. Please enter upload, download, or exit.")
            continue


if __name__ == "__main__":
    main()

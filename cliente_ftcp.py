import socket
import os
import sys

SERVER_ADDRESS = "127.0.0.1"
UDP_PORT = 5002
DOWNLOAD_DIR = "./downloads"

def request_file(protocol, file_name):
    # Cria a pasta de destino se não existir
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    dest_path = os.path.join(DOWNLOAD_DIR, file_name)

    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message = f"REQUEST,{protocol},{file_name}"
    udp_sock.sendto(message.encode('utf-8'), (SERVER_ADDRESS, UDP_PORT))
    response, _ = udp_sock.recvfrom(1024)
    response = response.decode('utf-8')
    print(f"Resposta UDP: {response}")
    udp_sock.close()

    if not response.startswith("RESPONSE"):
        print("Erro na negociação UDP. Verifique o protocolo ou o arquivo solicitado.")
        return

    _, _, transfer_port, _ = response.split(',')

    if protocol == "TCP":
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_sock.connect((SERVER_ADDRESS, int(transfer_port)))
        tcp_sock.sendall(f"get,{file_name}".encode('utf-8'))

        with open(dest_path, 'wb') as f:
            while True:
                chunk = tcp_sock.recv(1024)
                if not chunk:
                    break
                f.write(chunk)

        print(f"Arquivo {file_name} recebido com sucesso via TCP.")
        tcp_sock.sendall(f"ftcp_ack,{os.path.getsize(dest_path)}".encode('utf-8'))
        tcp_sock.close()

    elif protocol == "UDP":
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.sendto(f"get,{file_name}".encode('utf-8'), (SERVER_ADDRESS, int(transfer_port)))

        with open(dest_path, 'wb') as f:
            while True:
                chunk, _ = udp_sock.recvfrom(1024)
                if chunk == b"END":
                    break
                f.write(chunk)

        print(f"Arquivo {file_name} recebido com sucesso via UDP.")
        udp_sock.close()
        sys.exit(0)

if __name__ == '__main__':
    protocol = input("Escolha o protocolo (TCP/UDP): ").strip().upper()
    file_name = input("Escolha o arquivo (a.txt/b.txt): ").strip()
    request_file(protocol, file_name)

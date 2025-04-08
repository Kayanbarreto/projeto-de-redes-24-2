import socket
import threading
import os

CONFIG = {
    "TCP_PORT": 5001,
    "UDP_PORT": 5002,  
    "UDP_TRANSFER_PORT": 5003,  
    "FILE_A": "a.txt",
    "FILE_B": "b.txt"
}

def handle_udp_negotiation():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(('0.0.0.0', CONFIG["UDP_PORT"]))
    print(f"Servidor de negociação UDP escutando na porta {CONFIG['UDP_PORT']}")

    while True:
        data, addr = udp_sock.recvfrom(1024)
        message = data.decode('utf-8')
        print(f"Mensagem recebida do UDP: {message} de {addr}")

        try:
            command, protocol, file_name = message.split(',')
            if protocol not in ["TCP", "UDP"]:
                response = "ERROR,PROTOCOLO INVALIDO,,"
            elif file_name not in [CONFIG["FILE_A"], CONFIG["FILE_B"]]:
                response = "ERROR,ARQUIVO NAO ENCONTRADO,,"
            else:
                transfer_port = CONFIG["TCP_PORT"] if protocol == "TCP" else CONFIG["UDP_TRANSFER_PORT"]
                response = f"RESPONSE,{protocol},{transfer_port},{file_name}"
        except ValueError:
            response = "ERROR,FORMATO INVALIDO,,"

        udp_sock.sendto(response.encode('utf-8'), addr)

def handle_tcp_transfer(conn, addr):
    print(f"Cliente TCP conectado de {addr}")
    try:
        data = conn.recv(1024).decode('utf-8')
        print(f"Mensagem recebida do TCP: {data} de {addr}")

        if data.startswith("get,"):
            file_name = data.split(',')[1]
            if file_name in ["a.txt", "b.txt"]:
                file_path = CONFIG["FILE_A"] if file_name == "a.txt" else CONFIG["FILE_B"]
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        while chunk := f.read(1024):
                            conn.sendall(chunk)
                    print(f"Arquivo {file_name} enviado para {addr}")
                else:
                    conn.sendall(b"ERROR,ARQUIVO NAO ENCONTRADO")
        elif data.startswith("ftcp_ack,"):
            print(f"ACK recebida de {addr}: {data}")
    finally:
        conn.close()
        print(f"Cliente TCP desconectado de {addr}")

def handle_udp_transfer(file_name, addr, udp_sock):
    file_path = CONFIG["FILE_A"] if file_name == "a.txt" else CONFIG["FILE_B"]
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            while chunk := f.read(1024):
                udp_sock.sendto(chunk, addr)
        print(f"Arquivo {file_name} enviado via UDP para {addr}")
        udp_sock.sendto(b"END", addr)  
    else:
        udp_sock.sendto(b"ERROR,ARQUIVO NAO ENCONTRADO", addr)

def tcp_server():
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.bind(('0.0.0.0', CONFIG["TCP_PORT"]))
    tcp_sock.listen(5)
    print(f"Servidor TCP escutando na porta {CONFIG['TCP_PORT']}")

    while True:
        conn, addr = tcp_sock.accept()
        threading.Thread(target=handle_tcp_transfer, args=(conn, addr)).start()

def udp_transfer_server():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(('0.0.0.0', CONFIG["UDP_TRANSFER_PORT"]))  # Use a nova porta
    print(f"Servidor de transferência UDP escutando na porta {CONFIG['UDP_TRANSFER_PORT']}")

    while True:
        data, addr = udp_sock.recvfrom(1024)
        message = data.decode('utf-8')
        print(f"Mensagem recebida para transferência UDP: {message} de {addr}")

        if message.startswith("get,"):
            file_name = message.split(',')[1]
            handle_udp_transfer(file_name, addr, udp_sock)

if __name__ == '__main__':
    threading.Thread(target=handle_udp_negotiation, daemon=True).start()
    threading.Thread(target=tcp_server, daemon=True).start()
    threading.Thread(target=udp_transfer_server, daemon=True).start()

    print("Servidor FTCP rodando. Pressione Ctrl+C para encerrar.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Servidor encerrado.")
import socket
import configparser
import threading

config = configparser.ConfigParser()
config.read('config.ini')

UDP_PORT = int(config['CLIENT']['udp_port'])
TCP_PORT_A = int(config['TRANSFER']['tcp_port_a'])
TCP_PORT_B = int(config['TRANSFER']['tcp_port_b'])

FILE_PATHS = {
    "a.txt": config['FILES']['a'],
    "b.txt": config['FILES']['b']
}

# Envia o arquivo solicitado por TCP
def handle_tcp_connection(tcp_port, nome_arquivo):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.bind(('', tcp_port))
        tcp_socket.listen(1)
        print(f"[TCP] Aguardando conexão na porta {tcp_port} para {nome_arquivo}...")

        conn, addr = tcp_socket.accept()
        with conn:
            print(f"[TCP] Conexão estabelecida com {addr}")
            data = conn.recv(1024).decode()
            print(f"[TCP] Comando recebido: {data}")
            if data.startswith("get"):
                _, arquivo = data.split(",")
                if arquivo in FILE_PATHS:
                    with open(FILE_PATHS[arquivo], 'rb') as f:
                        conteudo = f.read()
                        conn.sendall(conteudo)
                        print(f"[TCP] Arquivo {arquivo} enviado ({len(conteudo)} bytes)")

                        conn.shutdown(socket.SHUT_WR)

                    ack = conn.recv(1024).decode()
                    print(f"[TCP] Confirmação recebida: {ack}")
                else:
                    conn.sendall(b"ERRO: Arquivo nao encontrado")
                    print(f"[TCP] Arquivo {arquivo} nao encontrado")

# Escuta UDP para negociação
def udp_negociacao():
    print("[INICIANDO SERVIDOR UDP]")  

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.bind(('', UDP_PORT))
        print(f"[UDP] Servidor escutando na porta {UDP_PORT}...")

        while True:
            mensagem, addr = udp_socket.recvfrom(1024)
            decoded = mensagem.decode()
            print(f"[UDP] Mensagem recebida de {addr}: {decoded}")

            if decoded.startswith("REQUEST"):
                try:
                    _, protocolo, nome_arquivo = decoded.split(",")
                except ValueError:
                    erro = "ERROR,Formato_invalido"
                    udp_socket.sendto(erro.encode(), addr)
                    continue

                if protocolo != "TCP":
                    erro = "ERROR,Protocolo_nao_suportado"
                    udp_socket.sendto(erro.encode(), addr)
                    print(f"[UDP] Protocolo não suportado: {protocolo}")
                    continue

                if nome_arquivo == "a.txt":
                    porta_tcp = TCP_PORT_A
                elif nome_arquivo == "b.txt":
                    porta_tcp = TCP_PORT_B
                else:
                    erro = "ERROR,Arquivo_nao_encontrado"
                    udp_socket.sendto(erro.encode(), addr)
                    print(f"[UDP] Arquivo não encontrado: {nome_arquivo}")
                    continue

                resposta = f"RESPONSE,{porta_tcp},{nome_arquivo}"
                udp_socket.sendto(resposta.encode(), addr)
                print(f"[UDP] Resposta enviada: {resposta}")

                # Iniciar thread TCP
                thread_tcp = threading.Thread(target=handle_tcp_connection, args=(porta_tcp, nome_arquivo))
                thread_tcp.start()

# Início do servidor
if __name__ == '__main__':
    udp_negociacao()

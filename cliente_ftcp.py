import socket
import configparser
import os

config = configparser.ConfigParser()
config.read('config.ini')

SERVER_IP = config['CLIENT']['server_ip']
UDP_PORT = int(config['CLIENT']['udp_port'])
SAVE_PATH = config['TRANSFER']['save_path']

# Função para negociar via UDP
def negociar_udp(nome_arquivo):
    mensagem = f"REQUEST,TCP,{nome_arquivo}"
    print(f"[CLIENTE] Enviando mensagem UDP: {mensagem}")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.sendto(mensagem.encode(), (SERVER_IP, UDP_PORT))
        resposta, _ = udp_socket.recvfrom(1024)
        print(f"[CLIENTE] Resposta UDP recebida: {resposta.decode()}")
        return resposta.decode()

# Função para realizar a transferência via TCP
def transferir_tcp(tcp_port, nome_arquivo):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.connect((SERVER_IP, tcp_port))
        print(f"[CLIENTE] Conectado ao servidor TCP na porta {tcp_port}")
        tcp_socket.sendall(f"get,{nome_arquivo}".encode())
        print(f"[CLIENTE] Comando enviado: get,{nome_arquivo}")

        dados_recebidos = b''
        print("[CLIENTE] Aguardando dados do servidor...")

        while True:
            segmento = tcp_socket.recv(1024)
            if not segmento:
                print("[CLIENTE] Fim dos dados recebido (socket fechado).")
                break
            print(f"[CLIENTE] Segmento recebido: {len(segmento)} bytes")
            dados_recebidos += segmento

        print(f"[CLIENTE] Total de bytes recebidos: {len(dados_recebidos)}")

        ack = f"ftcp_ack,{len(dados_recebidos)}"
        tcp_socket.sendall(ack.encode())
        print(f"[CLIENTE] Confirmação enviada: {ack}")

    return dados_recebidos

if __name__ == '__main__':
    arquivo = input("Qual arquivo deseja? (a.txt ou b.txt): ").strip()

    resposta = negociar_udp(arquivo)

    if resposta.startswith("RESPONSE"):
        _, porta_tcp_str, nome_arquivo = resposta.split(",")
        porta_tcp = int(porta_tcp_str)
        print(f"[CLIENTE] Iniciando transferência de {nome_arquivo} pela porta TCP {porta_tcp}")
        conteudo = transferir_tcp(porta_tcp, nome_arquivo)

        try:
            os.makedirs(SAVE_PATH, exist_ok=True)
            caminho_completo = os.path.join(SAVE_PATH, nome_arquivo)
            with open(caminho_completo, 'wb') as f:
                f.write(conteudo)
            print(f"[CLIENTE] Arquivo {nome_arquivo} salvo com sucesso em '{caminho_completo}'")
        except Exception as e:
            print(f"[CLIENTE] ERRO ao salvar o arquivo: {e}")
    else:
        print("[CLIENTE] Erro na negociação:", resposta)


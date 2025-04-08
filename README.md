# Projeto: Protocolo de Transferência de Arquivos Personalizado – FTCP

Projeto de Redes para implementação de um protocolo personalizado de transferência de arquivos utilizando UDP e TCP.

---

## 📚 Visão Geral

Este projeto implementa um sistema cliente-servidor que realiza a transferência de arquivos utilizando um protocolo próprio (FTCP). A negociação inicial acontece via **UDP**, e a transferência ocorre via **TCP**, com confirmação de recebimento.

---

## 👨‍💻 Equipe

- Integrante 1: [Nome do Aluno 1]
- Integrante 2: [Nome do Aluno 2]
- Integrante 3: [Nome do Aluno 3]
- Integrante 4: [Nome do Aluno 4]

---

## 🗂️ Estrutura do Projeto

```
projeto-de-redes/
├── cliente_ftcp.py
├── servidor_ftcp.py
├── config.ini
├── a.txt
├── b.txt
├── downloads/
│   └── (arquivos recebidos)
├── README.md
```

---

## ⚙️ Como Executar

### 1. Configuração

Verifique o arquivo `config.ini` com os seguintes parâmetros:

```ini
[CLIENT]
server_ip = 127.0.0.1
udp_port = 5002

[FILES]
a = ./a.txt
b = ./b.txt

[TRANSFER]
save_path = ./downloads/
tcp_port_a = 5001
tcp_port_b = 5003
```

Certifique-se de que os arquivos `a.txt` e `b.txt` existem e têm conteúdo.

---

### 2. Executando o servidor

Abra um terminal na pasta do projeto e execute:

```bash
python servidor_ftcp.py
```

Você verá:

```
[UDP] Servidor escutando na porta 5002...
```

---
### 3. Executando o cliente

Abra um segundo terminal e execute:

```bash
python cliente_ftcp.py
```

Digite `a.txt` ou `b.txt` quando solicitado.

---

### 4. Resultado Esperado

- O cliente solicita o arquivo via UDP.
- O servidor responde com a porta TCP.
- O cliente conecta via TCP e solicita o arquivo.
- O servidor envia o arquivo e aguarda confirmação.
- O cliente salva o arquivo na pasta `downloads/`.

---

## 📦 Arquivos de Teste

- `a.txt`: Conteúdo fictício para teste de transferência.
- `b.txt`: Segundo arquivo de teste.

---

## 📡 Captura com Wireshark (opcional)

Para capturar o tráfego FTCP:

1. Inicie o Wireshark.
2. Selecione a interface correta (ex: Loopback).
3. Inicie a gravação.
4. Execute cliente e servidor normalmente.
5. Pare e salve a captura como `.pcapng`.

---

## 📌 Observações

- Protocolo FTCP suporta apenas `TCP` nesta versão.
- Mensagens seguem o formato:
  - UDP: `REQUEST,TCP,a.txt`
  - UDP Resposta: `RESPONSE,5001,a.txt`
  - TCP: `get,a.txt`
  - Confirmação: `ftcp_ack,<bytes_recebidos>`

---

## ✅ Status

✅ Implementação completa  
✅ Testes realizados com sucesso  
✅ Pronto para análise via Wireshark

---

## 📁 Licença

Projeto acadêmico – uso livre para fins educacionais.

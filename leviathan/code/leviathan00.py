import os
import pwn

import re

from bs4 import BeautifulSoup

pwn.context.log_level = "WARNING"

n = os.path.basename(__file__)
n = n.split(".")[0]
n = n[n.find("leviathan")+len("leviathan"):]

n = int(n)

username = f"leviathan{n}"
hostname = "leviathan.labs.overthewire.org"
password = None 

with open(f"./leviathan/password/leviathan{n:02}-password.txt") as f:
    password = f.read()

print(f"Connecting to {hostname}:2223")
print(f"Username : {username}")
print(f"Password : {password}")
print() 

connect = pwn.ssh(host=hostname, user=username, password=password, port=2223)

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

def send_lines_remote(lines: list[str] | list[bytes], remote: pwn.tubes.ssh.ssh_connecter | pwn.tubes.ssh.ssh_channel) -> None:
    if type(lines[0]) == str:
        lines = [s.encode() for s in lines]

    print(f"Sending {len(lines)} lines", end="...")
    remote.sendlines(lines)
    print("Done")

    print()

def receive_output(channel: pwn.tubes.ssh.ssh_channel | pwn.tubes.ssh.ssh_connecter, lines: int = None, all: bool = False) -> str:
    output = None
    
    print("Receiving output", end="...")
    try:
        if not lines:
            output = channel.recvall() if all else channel.recv()
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

def filter_escape(s: str, allowed: list[str] = [" "]) -> str:
    regex = r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]'
    s = re.sub(regex, '', s)

    res = ""
    i = 0

    while i < len(s):
        if s[i] == "\x1b":
            i += 2
        else:
            res += s[i]
            i += 1

    res = "".join([*filter(lambda t: t and t.isalnum() or t in allowed, res)])

    return res

def save_password(result: str) -> str:
    print(f"Password Found : {result.__repr__()}")

    dir = f"./leviathan/password/leviathan{int(n)+1:02}-password.txt"

    print(f"Saving password to {dir}", end="...")

    with open(dir, "w+") as f:
        f.write(result)

    print("Done")

    print()

    return dir

if connect.connected():
    channel = send_command(["ls", "-la"])
    files = receive_output(channel, all=True)
    
    files = files.splitlines()[1:]
    files = [f.split() for f in files]
    files = [f for f in files if "leviathan" in f[3]]

    dir = files[0][-1]

    channel = send_command(["ls", dir])
    file = receive_output(channel)

    channel = send_command(["cd", dir, "&&", "cat", file])
    content = receive_output(channel, all=True)

    print("HTML File found, saving to local directory", end="...")
    
    with open(f"./leviathan/code/leviathan{n:02}-file.html", "w+") as f:
        f.write(content)

    print("Done\n")

    content = content.splitlines()
    content = [c for c in content if "password" in c][0]

    soup = BeautifulSoup(content, features="html.parser")
    soup = soup.find("a")

    link = soup.attrs["href"]

    result = link.split()
    result = result[-1]

    connect.close()

save_password(result)
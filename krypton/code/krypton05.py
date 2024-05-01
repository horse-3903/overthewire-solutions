import os
import pwn

import re

from collections import Counter

pwn.context.log_level = "WARNING"

n = os.path.basename(__file__)
n = n.split(".")[0]
n = n[n.find("krypton")+7:]

n = int(n)

username = f"krypton{n}"
hostname = "krypton.labs.overthewire.org"
password = None 

with open(f"./krypton/password/krypton{n:02}-password.txt") as f:
    password = f.read()

print(f"Connecting to {hostname}:2231")
print(f"Username : {username}")
print(f"Password : {password}")
print() 

connect = pwn.ssh(host=hostname, user=username, password=password, port=2231)

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

    dir = f"./krypton/password/krypton{int(n)+1:02}-password.txt"

    print(f"Saving password to {dir}", end="...")

    with open(dir, "w+") as f:
        f.write(result)

    print("Done")

    return dir

def rot(s: str, n: int) -> str:
    res = ""

    for c in s:
        if not c.isalpha():
            res += c
        else:
            res += chr((ord(c) - 65 + n) % 26 + 65)

    return res

if connect.connected():
    dir = f"/krypton/krypton{n}/"
    
    channel = send_command(command=["ls", dir])
    files = receive_output(channel=channel)

    files = files.split()
    cipher_file = [f for f in files if "krypton" in f]

    channel = send_command(command=["cat", os.path.join(dir, cipher_file[0])])
    cipher = receive_output(channel=channel)

    key_len = 1 # change this
    
    files = [f for f in files if "found" in f]

    # for key_len in range(1, 20):
    while True:
        print(f"Trying Key Length : {key_len}")
        print()
        total_text = {i: [] for i in range(key_len)}

        for f in files:
            channel = send_command(command=["cat", os.path.join(dir, f)])
            output = receive_output(channel=channel)

            output = output.replace(" ", "")

            for i in range(key_len):
                total_text[i] += [char for idx, char in enumerate(output) if idx % key_len == i]

        rot_dict = {}
        
        for i in total_text.keys():
            total_text[i] = "".join(total_text[i])

        print("Finding key : ")
        
        for i, v in total_text.items():
            print(f"Checking key position : {i}")

            for j in range(26):
                text = rot(v, j)

                common = Counter(text).most_common()

                if common[0][0] == "E":
                    rot_dict[i] = j
                    print(f"Rotation found for key position {i} : {j}")
                    print()
                    break

        print("Constructing password", end="...")

        cipher = cipher.replace(" ", "")

        result = ""
        
        for i, c in enumerate(cipher):
            result += rot(c, rot_dict[i % key_len])
        
        print("Done\n")

        print(f"Constructed Password : {result}")

        success = False

        while True:
            print(f"Testing {result.__repr__()}", end="...")
            
            try:
                connect = pwn.ssh(host=hostname, user=f"krypton{n+1}", password=result, port=2231)
                print("Success")
                
                success = True

                break
            except Exception as e:
                e = str(e)
                print(f"Failed : {e.strip('.')[:e.find('[') if '[' in e else len(e)]}")
                
                if "Authentication" in e:
                    key_len += 1
                    break
            
            print()

        if success:
            break

    dir = save_password(result)
    
    connect.close()
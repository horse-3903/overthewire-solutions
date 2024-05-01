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
        try:
            output = output.decode()
        except Exception as e:
            print(e)

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
    
    files = [f for f in files if not any(t in f for t in ["HINT", "README", "krypton"])]

    for f in files:
        channel = send_command(command=["cat", os.path.join(dir, f)])
        output = receive_output(channel=channel)

    tmp_dir = "/tmp/horse3903/"

    channel = send_command(command=["rm", "-rf", tmp_dir])

    channel = send_command(command=["mkdir", tmp_dir])

    # test encryption function
    
    # first test
    query1 = "A"*100

    channel = send_command(command=["cd", dir, "&&", "echo", query1.__repr__(), ">", os.path.join(tmp_dir, "input1.txt")])
    
    channel = send_command(command=["cd", dir, "&&", "touch", os.path.join(tmp_dir, "output1.txt")])

    channel = send_command(command=["cd", dir, "&&", "./encrypt6", os.path.join(tmp_dir, "input1.txt"), os.path.join(tmp_dir, "output1.txt")])

    channel = send_command(command=["cd", dir, "&&", "cat", os.path.join(tmp_dir, "output1.txt")])
    output1 = receive_output(channel=channel)

    print(query1, output1)

    print()

    # second test
    query2 = "B"*100

    channel = send_command(command=["cd", dir, "&&", "echo", query2.__repr__(), ">", os.path.join(tmp_dir, "input2.txt")])
    
    channel = send_command(command=["cd", dir, "&&", "touch", os.path.join(tmp_dir, "output2.txt")])

    channel = send_command(command=["cd", dir, "&&", "./encrypt6", os.path.join(tmp_dir, "input2.txt"), os.path.join(tmp_dir, "output2.txt")])

    channel = send_command(command=["cd", dir, "&&", "cat", os.path.join(tmp_dir, "output2.txt")])
    output2 = receive_output(channel=channel)

    print(query2, output2)

    print()

    print(f"Test 1 : {output1}")
    print(f"Test 2 : {output2}")
    print()

    if output2 == rot(output1, 1):
        print("Output 2 is Output 1 shifted by 1 letter")

    print()

    key = "EICTDGYIYZKTHNSIRFXYCPFUEOCKRN"

    print(f"Repeated Key : {key}")
    print()

    result = ""

    for i in range(len(cipher)):
        k = ord(cipher[i]) - ord(key[i])
        if k < 0: 
            k += 26
        
        k += ord('A')

        result += chr(k)
    
    dir = save_password(result)
    
    connect.close()

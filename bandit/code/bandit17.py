import os
import pwn

from paramiko.ssh_exception import AuthenticationException

import re

pwn.context.log_level = "WARNING"

n = os.path.basename(__file__)
n = n.split(".")[0]
n = n[n.find("bandit")+6:]

username = f"bandit{n}"
hostname = "bandit.labs.overthewire.org"
password = None

print(f"Connecting to {hostname}:2220")
print(f"Username : {username}")
print(f"SSH Key : ./bandit/password/{username}-sshkey.private")
print()

connect = pwn.ssh(host=hostname, user=username, keyfile=f"./bandit/password/{username}-sshkey.private", port=2220)

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
    channel = send_command(["ls"])
    files = receive_output(channel)
    file1, file2 = files.split()

    channel = send_command(["diff", file1, file2])
    result = receive_output(channel).split("\n")
    result = [re.findall("[A-Za-z0-9]", line) for line in result]
    result = ["".join(line) for line in result]
    result = [*filter(lambda line: line, result)]

    for line in result:
        print(f"Testing Password : {line}", end="...")

        try:
            test_connect = pwn.ssh(host=hostname, user=f"{username[:-1]}{int(username[-1])+1}", password=line, port=2220)
            result = line
            test_connect.close()

            print("Success")
            break
        except AuthenticationException:
            print("Failed")

with open(f"./bandit/password/{username[:-1]}{int(username[-1])+1}-password.txt", "w+") as f:
    f.write(result)
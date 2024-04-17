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
    output = channel.recv()
    output = output.decode()

    output = output.strip()
    output = output.strip("\n")
    print("Done")

    print(output)
    print()

    return output

if connect.connected():
    channel = send_command(["ls"])
    identity_file = receive_output(channel)

    channel = send_command(["cat", identity_file])
    result = receive_output(channel)

    with open(f"./bandit/password/{username[:6]}{int(username[6:])+1}-sshkey.private", "w+") as f:
        f.write(result)

    connect.close()

print(f"Connecting to {hostname}:2220")
print(f"Username : {username[:6]}{int(username[6:])+1}")
print(f"SSH Key : ./bandit/password/{username[:6]}{int(username[6:])+1}-sshkey.private")

connect = pwn.ssh(host=hostname, user=f"{username[:6]}{int(username[6:])+1}", password=password, port=2220, keyfile=f"./bandit/password/{username[:6]}{int(username[6:])+1}-sshkey.private")

if connect.connected():
    channel = send_command(["ls", "/etc/bandit_pass"], connect)
    file = receive_output(channel)

    channel = send_command(["cat" , os.path.join("/etc/bandit_pass/", "bandit14")], connect)
    result = receive_output(channel)

    connect.close()

with open(f"./bandit/password/bandit{int(n)+1}-password.txt", "w+") as f:
    f.write(result)
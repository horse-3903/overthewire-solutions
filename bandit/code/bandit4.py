import os
import pwn

pwn.context.log_level = "WARNING"

n = os.path.basename(__file__)
n = n[n.find("bandit")+6]

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

def send_command(command: str) -> pwn.tubes.ssh.ssh_channel:
    print(f"Sending process : `{command}`", end="...")
    channel = connect.system(command)
    print("Done")
    
    print()

    return channel

def receive_output(channel: pwn.tubes.ssh.ssh_channel) -> str:
    print("Receiving output", end="...")
    output = channel.recv()
    output = output.decode()

    output = output.replace("\n", " ")
    output = output.strip()
    print("Done")

    print(output)
    print()

    return output

if connect.connected():
    # find all files in current directory
    channel = send_command("ls")
    result = receive_output(channel)

    channel = send_command(f"ls {result}")
    files = receive_output(channel)
    files = [f"{result}/{f}" for f in files.split()]

    for f in files:
        channel = send_command(f"file {f}")
        result = receive_output(channel)

        if "ASCII text" in result:
            break

    channel = send_command(f"cat {f}")
    result = receive_output(channel)

    connect.close()

with open(f"./bandit/password/{username[:-1]}{int(username[-1])+1}-password.txt", "w+") as f:
    f.write(result)
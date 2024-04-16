import os
import pwn

pwn.context.log_level = "WARNING"

n = os.path.basename(__file__)
n = n[n.find("bandit")+6]

username = f"bandit{n}"
hostname = "bandit.labs.overthewire.org"
password = "bandit0"

print(f"Connecting to {hostname}:2220")
print(f"Username : {username}")
print(f"Password : {password}")
print()

connect = pwn.ssh(host=hostname, user=username, password=password, port=2220)

def send_command(command: list[str]) -> pwn.tubes.ssh.ssh_channel:
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

    output = output.strip("\n")
    print("Done")

    print(output)
    print()

    return output

if connect.connected():
    # find all files in current directory
    channel = send_command(["ls"])

    files = receive_output(channel)
    files = files.split()

    for f in files:
        # read file data
        channel = send_command(["cat", f])

        result = receive_output(channel)

    connect.close()

with open(f"./bandit/password/{username[:-1]}{int(username[-1])+1}-password.txt", "w+") as f:
    f.write(result)
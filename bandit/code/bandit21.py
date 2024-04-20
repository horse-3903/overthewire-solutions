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
    command = map(str, command)
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
    dir = "/etc/cron.d/"
    
    channel = send_command(["ls", dir])
    
    files = receive_output(channel)
    files = files.replace("\n", " ")
    files = files.split()

    for f in files:
        if f"bandit{int(n)+1}" in f:
            file = f
            break
    
    channel = send_command(["cat", os.path.join(dir, file)])
    command = receive_output(channel)
    command = command.splitlines()[-1]
    command = command.split()
    command = [*dict.fromkeys(command).keys()]

    for c in command:
        channel = send_command(["cat", c])

        try:
            result = receive_output(channel)

            if any(t in result.lower() for t in ["no such file or directory", "error", "permission denied"]):
                raise FileNotFoundError
            else:
                break
        except:
            continue

    command = result.splitlines()
    command = command[-1].split()

    for c in command:
        channel = send_command(["cat", c])

        try:
            result = receive_output(channel)

            if any(t in result.lower() for t in ["no such file or directory", "error", "permission denied"]):
                raise FileNotFoundError
            else:
                break
        except:
            continue

    connect.close()

with open(f"./bandit/password/bandit{int(n)+1}-password.txt", "w+") as f:
    f.write(result)
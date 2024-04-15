import pwn

pwn.context.log_level = "WARNING"

n = 2
username = f"bandit{n}"
hostname = "bandit.labs.overthewire.org"
password = None

with open(f"./bandit/password/{username}-password.txt") as f:
    password = f.read()

print(f"Connecting to {hostname}:2220")
print(f"Username : {username}")
print(f"Password : {password}")

connect = pwn.ssh(host=hostname, user=username, password=password, port=2220)

def send_command(command: str) -> pwn.tubes.ssh.ssh_channel:
    print(f"Sending process : `{command}`", end="...")
    channel = connect.system(command)
    print("Done")

    return channel

def receive_output(channel: pwn.tubes.ssh.ssh_channel) -> bytes:
    print("Receiving output", end="...")
    output = channel.recvline(keepends=False)
    print("Done")

    print(output.decode())

    return output

if connect.connected():
    # find all files in current directory
    channel = send_command("ls")

    files = [receive_output(channel).decode()]

    for f in files:
        # read file data
        if f[0] == " ":
            channel = send_command(f'cat "{f}"')
        else:
            channel = send_command(f"cat {f}")

        result = receive_output(channel).decode()

    connect.close()

with open(f"./bandit/password/{username[:-1]}{int(username[-1])+1}-password.txt", "w+") as f:
    f.write(result)
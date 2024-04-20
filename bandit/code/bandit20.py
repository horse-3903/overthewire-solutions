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

connect1 = pwn.ssh(host=hostname, user=username, password=password, port=2220)
connect2 = pwn.ssh(host=hostname, user=username, password=password, port=2220)

def send_command(command: list[str], connect: pwn.ssh) -> pwn.tubes.ssh.ssh_channel:
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

if connect1.connected() and connect2.connected():
    port = 3903

    # network daemon
    channel1 = send_command(["nc", "-l", port], connect1)
    channel1.sendline(password.encode())

    # suconnect
    channel2 = send_command(["ls"], connect2)
    file = receive_output(channel2)

    channel2 = send_command([f"./{file}", port], connect2)

    result1 = receive_output(channel1)
    result2 = receive_output(channel2)

    connect1.close()

with open(f"./bandit/password/bandit{int(n)+1}-password.txt", "w+") as f:
    f.write(result1)
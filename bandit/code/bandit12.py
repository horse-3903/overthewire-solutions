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
    file = receive_output(channel)

    dir = "/tmp/horse3903/"

    channel = send_command(["rm", "-r", dir])
    channel = send_command(["mkdir", dir])
    channel = send_command(["cp", file, dir])

    # rename
    channel = send_command(["mv", os.path.join(dir, file), os.path.join(dir, "data0.txt")])

    active_file = "data0.txt"

    # 1st decompression
    channel = send_command(["file", os.path.join(dir, active_file)])
    result = receive_output(channel)

    channel = send_command(["xxd", "-r", os.path.join(dir, active_file), ">", os.path.join(dir, "data1.txt")])

    active_file = "data1.txt"

    # 2nd decompression
    channel = send_command(["file", os.path.join(dir, active_file)])
    result = receive_output(channel)

    channel = send_command(["mv", os.path.join(dir, active_file), os.path.join(dir, active_file + ".gz")])
    active_file = active_file + ".gz"

    channel = send_command(["gunzip", "-c", os.path.join(dir, active_file), ">", os.path.join(dir, "data2.txt")])

    active_file = "data2.txt"

    # 3rd decompression
    channel = send_command(["file", os.path.join(dir, active_file)])
    result = receive_output(channel)

    channel = send_command(["mv", os.path.join(dir, active_file), os.path.join(dir, active_file + ".bz2")])
    active_file = active_file + ".bz2"

    channel = send_command(["bzip2", "-d", os.path.join(dir, active_file)])

    channel = send_command(["mv", os.path.join(dir, active_file[:-4]), os.path.join(dir, "data3.txt")])
    active_file = "data3.txt"

    # 4th decompression
    channel = send_command(["file", os.path.join(dir, active_file)])
    result = receive_output(channel)

    channel = send_command(["mv", os.path.join(dir, active_file), os.path.join(dir, active_file + ".gz")])
    active_file = active_file + ".gz"

    channel = send_command(["gunzip", "-c", os.path.join(dir, active_file), ">", os.path.join(dir, "data4.txt")])
    active_file = "data4.txt"

    # 5th decompression
    channel = send_command(["file", os.path.join(dir, active_file)])
    result = receive_output(channel)

    channel = send_command(["mv", os.path.join(dir, active_file), os.path.join(dir, active_file + ".tar")])
    active_file = active_file + ".tar"

    channel = send_command(["cd", dir, "&&", "tar", "-xf", os.path.join(dir, active_file)])

    channel = send_command(["ls", dir])
    file = receive_output(channel).split()
    file = sorted(file)
    
    active_file = file[-1]

    # 6th decompression
    channel = send_command(["file", os.path.join(dir, active_file)])
    result = receive_output(channel)

    channel = send_command(["mv", os.path.join(dir, active_file), os.path.join(dir, active_file + ".tar")])
    active_file = active_file + ".tar"

    channel = send_command(["cd", dir, "&&", "tar", "-xf", os.path.join(dir, active_file)])

    channel = send_command(["ls", dir])
    file = receive_output(channel).split()
    file = sorted(file)
    
    active_file = file[-1]

    # 7th decompression
    channel = send_command(["file", os.path.join(dir, active_file)])
    result = receive_output(channel)

    channel = send_command(["mv", os.path.join(dir, active_file), os.path.join(dir, active_file + ".bz2")])
    active_file = active_file + ".bz2"

    channel = send_command(["bzip2", "-d", os.path.join(dir, active_file)])

    channel = send_command(["mv", os.path.join(dir, active_file[:-4]), os.path.join(dir, "data7.txt")])
    active_file = "data7.txt"

    # 8th decompression    
    channel = send_command(["file", os.path.join(dir, active_file)])
    result = receive_output(channel)

    channel = send_command(["mv", os.path.join(dir, active_file), os.path.join(dir, active_file + ".tar")])
    active_file = active_file + ".tar"

    channel = send_command(["cd", dir, "&&", "tar", "-xf", os.path.join(dir, active_file)])

    channel = send_command(["ls", dir])
    file = receive_output(channel).split()
    file = sorted(file)
    
    active_file = file[-1]

    # 9th decompression
    channel = send_command(["file", os.path.join(dir, active_file)])
    result = receive_output(channel)

    channel = send_command(["mv", os.path.join(dir, active_file), os.path.join(dir, active_file + ".gz")])
    active_file = active_file + ".gz"

    channel = send_command(["gunzip", "-c", os.path.join(dir, active_file), ">", os.path.join(dir, "data10.txt")])
    active_file = "data10.txt"

    # retrieve data
    channel = send_command(["file", os.path.join(dir, active_file)])
    result = receive_output(channel)

    channel = send_command(["cat", os.path.join(dir, active_file)])
    result = receive_output(channel).split()
    result = result[-1]

    # delete tmp subdirectory
    channel = send_command(["rm", "-r", dir]) # thank you for your service 🫡

    connect.close()

with open(f"./bandit/password/bandit{int(n)+1}-password.txt", "w+") as f:
    f.write(result)
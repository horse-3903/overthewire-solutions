import pwn

username = "bandit0"
hostname = "bandit.labs.overthewire.org"
password = "bandit0"

s = pwn.ssh(host=hostname, user=username, password=password, port=2220)

if s.connected():
    # find all files in current directory
    p = s.system("ls")

    files = p.recvline(keepends=False).decode()
    files = files.split()

    for f in files:
        # read file data
        p = s.system(f"cat {f}")

        d = p.recvline(keepends=False).decode()

    s.close()

with open(f"./bandit/password/{username[:-1]}{int(username[-1])+1}-password.txt", "w+") as f:
    f.write(d)
import pwn

pwn.context.log_level = "WARNING"

username = "bandit1"
hostname = "bandit.labs.overthewire.org"
password = None

with open(f"./bandit/password/{username}-password.txt") as f:
    password = f.read()

s = pwn.ssh(host=hostname, user=username, password=password, port=2220)

if s.connected():
    # find all files in current directory
    p = s.system("ls")

    files = p.recvline(keepends=False).decode()
    files = files.split()

    for f in files:
        # read file data
        if f[0] == "-":
            p = s.system(f"cat <{f}")
        else:
            p = s.system(f"cat {f}")

        d = p.recvline(keepends=False).decode()

    s.close()

with open(f"./bandit/password/{username[:-1]}{int(username[-1])+1}-password.txt", "w+") as f:
    f.write(d)

# learning point : 
#   - if file has '-' in front of filename, add '<' to access it
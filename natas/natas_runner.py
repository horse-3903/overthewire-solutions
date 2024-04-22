import os
import webbrowser
import pyperclip

print("Natas Challenge")
# level = int(input("Natas Level : "))

dir = os.listdir("./natas/password")
dir = sorted(dir)

latest = dir[-1]
latest = latest.split("-")[0]
latest = latest[latest.find("natas")+5:]

level = int(latest)

username = f"natas{level}"
password = None

with open(f"./natas/password/natas{level:02}-password.txt", "r") as f:
    password = f.read()

website = f"http://{username}.natas.labs.overthewire.org"

print()

print(f"Username : {username}")
print(f"Password : {password}")
print(f"Website : {website}")

print("Saving password to clipboard", end="...")
pyperclip.copy(password)
print("Done")

print()

print(f"Opening web browser to {website}", end="...")
webbrowser.open(website, 1)
print("Done")

print(f"Saving new password of next level : Natas{level+1:02}")
password = input("Input new password : ")

with open(f"./natas/password/natas{level+1:02}-password.txt", "w+") as f:
    f.write(password)
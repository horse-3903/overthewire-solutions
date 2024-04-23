import os
import requests

from bs4 import BeautifulSoup, Tag
from bs4 import Comment

file = os.path.basename(__file__).split(".")
file = file[0]
file = file[file.find("natas")+5:]

level = int(file)

username = f"natas{level}"
password = None
website = f"http://{username}.natas.labs.overthewire.org"

result = None

with open(f"./natas/password/natas{level:02}-password.txt", "r") as f:
    password = f.read()

def natas_connect(website: str, username: str, password: str, params: dict = None) -> Tag:
    print(f"Connecting to {website}")
    print(f"Username : {username}")
    print(f"Password : {password}")
    print()

    r = requests.get(website, auth=(username, password), params=params)

    print("Parsing HTML", end="...")
    soup = BeautifulSoup(r.content, "html.parser")
    print("Done\n")

    print("Retrieving <body> tag", end="...")
    body = soup.find("body")
    print("Done\n")

    print(body)
    print()

    return body

body = natas_connect(website=website, username=username, password=password)

print("Finding comments", end="...")
comments = body.find_all(string=lambda element: isinstance(element, Comment))
print("Done\n")

result = comments[0]
result = result.split()

result = result[-1]

print(f"Password found : {result}\n")

print(f"Saving to file ./natas/password/natas{level+1:02}-password.txt", end="...")
with open(f"./natas/password/natas{level+1:02}-password.txt", "w+") as f:
    f.write(result or "")
print("Done")

print()
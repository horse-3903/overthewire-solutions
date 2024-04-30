import os

import base64

n = os.path.basename(__file__)
n = n.split(".")[0]
n = n[n.find("krypton")+7:]

n = int(n)

def save_password(result: str) -> None:
    dir = f"./krypton/password/krypton{int(n)+1:02}-password.txt"

    print(f"Saving password to {dir}", end="...")

    with open(dir, "w+") as f:
        f.write(result)

    print("Done")

encoded_pass = "S1JZUFRPTklTR1JFQVQ="

result = base64.b64decode(encoded_pass)
result = result.decode()

save_password(result=result)
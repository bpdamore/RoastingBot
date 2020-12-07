import random

chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789?!@#$%_-*"

print("""
PASSWORD TIME!
--------------
""")

num = int(input("How many characters do you want?\n"))

pwd = ""

while len(pwd) < num:
    pwd+= random.choice(chars)
print(pwd)
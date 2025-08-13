import bcrypt

password = b"mein_passwort"
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
print(hashed.decode())

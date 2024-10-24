from werkzeug.security import generate_password_hash

password = "super_earth"
hashed_password = generate_password_hash(password)
print(hashed_password)

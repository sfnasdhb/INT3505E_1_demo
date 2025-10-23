from werkzeug.security import generate_password_hash

hash_password = generate_password_hash('password123')
print("Hashed password:", hash_password)
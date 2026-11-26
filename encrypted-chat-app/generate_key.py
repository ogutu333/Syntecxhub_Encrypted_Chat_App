import secrets
import base64

# Generate a 32-byte key (256 bits)
key = secrets.token_bytes(32)

# Encode the key for storage
encoded_key = base64.b64encode(key).decode()

with open("shared.key", "w") as key_file:
    key_file.write(encoded_key)

print("Encryption key generated.")
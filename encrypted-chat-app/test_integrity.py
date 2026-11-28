import base64

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from crypto_utils import load_key, encrypt_message, decrypt_message


# Load the existing shared encryption key
key = load_key()

# Original message
message = "This is a secure message."

print("[+] Original message:", message)

# Encrypt the message
encrypted_message = encrypt_message(message, key)

print("[+] Message encrypted successfully.")
print("[+] Original ciphertext:", encrypted_message)

# Decode the Base64 payload
tampered_data = bytearray(
    base64.b64decode(encrypted_message)
)

# Modify one byte of the ciphertext
tampered_data[12] ^= 1

# Encode the modified payload
tampered_message = base64.b64encode(
    tampered_data
).decode()

print("\n[!] Tampering with encrypted message...")

# Attempt to decrypt the modified message
try:
    decrypted = decrypt_message(tampered_message, key)

    print("[-] WARNING: Message decrypted:", decrypted)

except Exception as error:
    print("[+] SUCCESS: Tampering detected!")
    print("[+] AES-GCM rejected the modified message.")
    print("[+] Error:", type(error).__name__)

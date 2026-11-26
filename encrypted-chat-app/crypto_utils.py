import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def load_key(filename="shared.key"):
    with open(filename, "r") as key_file:
        encoded_key = key_file.read().strip()

    key = base64.b64decode(encoded_key, validate=True)

    if len(key) != 32:
        raise ValueError("AES-256 requires a 32-byte key.")

    return key

def encrypt_message(message, key):
    aes = AESGCM(key)

    # 12-byte nonce recommended for AES-GCM
    nonce = os.urandom(12)
    ciphertext = aes.encrypt(
        nonce,
        message.encode(),
        None
    )

    # Package nonce + ciphertext + authentication tag
    encrypted_data = nonce + ciphertext
    return base64.b64encode(encrypted_data).decode()

def decrypt_message(encrypted_data, key):
    raw_data = base64.b64decode(
        encrypted_data,
        validate=True
    )

    nonce = raw_data[:12]
    ciphertext = raw_data[12:]

    aes = AESGCM(key)

    plaintext = aes.decrypt(
        nonce,
        ciphertext,
        None
    )

    return plaintext.decode()
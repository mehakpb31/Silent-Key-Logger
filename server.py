from flask import Flask, request
from cryptography.fernet import Fernet
import os

app = Flask(__name__)

@app.route('/', methods=['POST'])
def receive_log_and_key():
    uid = request.form.get('uid')
    username = request.form.get('username')
    
    # Retrieve and save the log and key files
    log = request.files['log']
    key = request.files['key']

    log_filename = f'{uid}_{username}_log.txt'
    key_filename = f'{uid}_{username}_key.key'
    decrypted_log_filename = f'{uid}_{username}_decrypted_log.txt'

    # Save log and key files
    log.save(log_filename)
    key.save(key_filename)

    # Decrypt log using the received key
    with open(key_filename, 'rb') as kf:
        key_data = kf.read()
    cipher = Fernet(key_data)

    with open(log_filename, 'rb') as lf:
        encrypted_log_data = lf.read()

    # Decrypt the data
    decrypted_log_data = cipher.decrypt(encrypted_log_data)

    # Append the decrypted data to the existing decrypted log file
    with open(decrypted_log_filename, 'ab') as df:
        df.write(decrypted_log_data)
        df.write(b'\n')  # Add a newline for separation between entries

    return 'Log and key received and decrypted successfully', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

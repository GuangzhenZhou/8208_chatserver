#!/usr/bin/env python3

import socket
import argparse
import concurrent.futures
import hashlib
import os
import json
import psutil
import logging
import threading
from flask import Flask, jsonify

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

args = argparse.ArgumentParser(description="Chat server")
args.add_argument("addr", action="store", help="IP address")
args.add_argument("port", type=int, action="store", help="Port")
args_dict = vars(args.parse_args())


class Server:

    def __init__(self):
        self.clients = {}
        self.user_keys = {}

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((args_dict["addr"], args_dict["port"]))
        self.sock.listen(100)
        
        self.message_backup_dir = 'message_backups'
        os.makedirs(self.message_backup_dir, exist_ok=True)

    def identify_client(self, conn):
        conn.send(b"Send user_id")
        user_id = conn.recv(256)
        return user_id.decode()

    def authenticate_user(self, conn, user_id):
        conn.send(b"Send public key")
        public_key_bytes = conn.recv(4096)
        if hashlib.sha256(public_key_bytes).hexdigest() != user_id:
            conn.send(b"Public key does not match user id")

        public_key = serialization.load_pem_public_key(public_key_bytes)
        challenge = hashlib.sha256(os.urandom(1024)).hexdigest().encode()
        ciphertext = public_key.encrypt(
            challenge,
            padding.OAEP(padding.MGF1(algorithm=hashes.SHA256()),
                         hashes.SHA256(), None))
        conn.send(ciphertext)
        if conn.recv(256) == challenge:
            conn.send(b"User authenticated")
            return public_key_bytes
        else:
            conn.send(b"Authentication challenge failed")
            return None

    def command_handler(self, string, sender):
        if string[0:8] == "!SENDKEY":
            user_id = string[9:]
            self.clients[sender].send(self.user_keys[user_id])

    def route_message(self, msg, user_id):
        msg_obj = json.loads(msg)
        dest_conn = self.clients[msg_obj["dest"]]
        dest_conn.send(msg_obj["text"].strip().encode())
        with open(os.path.join(self.message_backup_dir, f'{user_id}.txt'), 'a') as f:
            f.write(msg.decode() + '\n')

    def client_handler(self, user_id, addr):
        conn = self.clients[user_id]

        while True:
            try:
                msg = conn.recv(4096)
                if msg:
                    print(f"<{addr[0]}> {msg}")
                    if msg.decode()[0] == "!":
                        self.command_handler(msg.decode(), user_id)
                    else:
                        self.route_message(msg, user_id)
                else:
                    del self.clients[user_id]
            except:
                continue

    def execute(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            while True:
                conn, addr = self.sock.accept()
                user_id = self.identify_client(conn)
                public_key = self.authenticate_user(conn, user_id)
                self.clients[user_id] = conn
                self.user_keys[user_id] = public_key
                print(f"{addr[0]} connected with id {user_id}")
                futures.append(
                    executor.submit(self.client_handler,
                                    user_id=user_id,
                                    addr=addr))

    def monitor(self):
        while True:
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent
            net_io = psutil.net_io_counters()
            logging.info(f"CPU usage: {cpu_usage}%")
            logging.info(f"Memory usage: {memory_usage}%")
            logging.info(f"Network IO: {net_io}")
            time.sleep(60)  # sleep for 60 seconds

if __name__ == "__main__":
        
    app = Flask(__name__)

    @app.route('/monitor')
    def monitor():
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        net_io = psutil.net_io_counters()
        return jsonify({
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'net_io': net_io,
        })

    def start_flask_app():
        app.run(host='0.0.0.0', port=5001)

    # Start the Flask app in a new thread
    flask_thread = threading.Thread(target=start_flask_app)
    flask_thread.start()
    
    ser = Server()
    ser.execute()

    
#!/bin/bash


echo "Starting the server..."
./shell/start_server.sh &
echo "Server started."

echo "Starting client1..."
./shell/start_client1.sh
echo "Client1 started."

echo "Starting client2..."
./shell/start_client2.sh
echo "Client2 started."

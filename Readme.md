# Pre-requirements

```
pipenv install

pipenv shell
```

# Generate a user

```
python testing/generate_users.py 2 password
```

# Start the server

```
python chatserver/server.py 127.0.0.1 3000
```

# Start the client

```
python testing/client.py 127.0.0.1 3000
```

Then type into the key file name and password

Next `!DESTINATION {userID}`
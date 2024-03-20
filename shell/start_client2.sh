#!/opt/homebrew/bin/expect

set username "1b0f494fc3635879cc305c778d51bf29bbec388ebdcd1bc1fe32340dea0edbc5"
set password "luke1234"

spawn python testing/client.py 127.0.0.1 3000

send "$username\r"

send "$password\r"

send "Hi\r"

!SENDFILE filed_text.txt

expect eof

#!/opt/homebrew/bin/expect

set username "74459a0e19a12f8e0cddf8683bea4f9dd82e1eb547c2dac17747b71712bd267d"
set password "luke1234"

spawn python testing/client.py 127.0.0.1 3000

send "$username\r"

send "$password\r"

send "!DESTINATION 1b0f494fc3635879cc305c778d51bf29bbec388ebdcd1bc1fe32340dea0edbc5\r"

expect eof

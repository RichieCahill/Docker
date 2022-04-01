#!/bin/bash
mypassword=$(cat /config/Secret/passwd)

groupadd r2r0m0c0
useradd -m -g r2r0m0c0 -G users -G sudo r2r0m0c0
chsh -s /bin/zsh r2r0m0c0
chown r2r0m0c0:r2r0m0c0 -R /home/r2r0m0c0/
echo "r2r0m0c0:$mypassword" | chpasswd
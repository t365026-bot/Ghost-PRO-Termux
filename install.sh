#!/data/data/com.termux/files/usr/bin/bash

clear
echo -e "\e[1;32m"
echo "  [+] GHOST PRO V13 INSTALLER"
echo "  [+] DEPLOYING CORE..."
echo -e "\e[0m"

pkg update && pkg upgrade -y
pkg install python git binutils -y

echo -e "\e[1;32m[+] INSTALLING DEPENDENCIES...\e[0m"
pip install flet cryptography flet_audio

echo -e "\e[1;32m[+] STARTING GHOST SERVER ON PORT 8550...\e[0m"
python main.py

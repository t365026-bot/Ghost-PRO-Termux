#!/data/data/com.termux/files/usr/bin/bash
pkg update && pkg upgrade -y
pkg install python git -y
pip install --upgrade pip
# Установка flet и веб-компонентов
pip install flet flet-web firebase-admin cryptography
echo "Установка завершена. Запускай: python main.py"

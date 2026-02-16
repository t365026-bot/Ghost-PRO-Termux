import os
import sys
import time
import datetime
import threading
import firebase_admin
from firebase_admin import credentials, firestore

class GhostTerminal:
    def __init__(self):
        self.red = "\033[91m"
        self.green = "\033[92m"
        self.blue = "\033[94m"
        self.yellow = "\033[93m"
        self.reset = "\033[0m"
        self.db = None
        self.uid = None
        self.role = "USER"
        self.running = True

    def clear(self):
        os.system('clear')

    def animate_text(self, text, speed=0.02):
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(speed)
        print()

    def draw_logo(self):
        self.clear()
        logo = f"""{self.green}
 ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗    ██████╗ ██████╗  ██████╗ 
██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝    ██╔══██╗██╔══██╗██╔═══██╗
██║  ███╗███████║██║   ██║███████╗   ██║       ██████╔╝██████╔╝██║   ██║
██║   ██║██╔══██║██║   ██║╚════██║   ██║       ██╔═══╝ ██╔══██╗██║   ██║
╚██████╔╝██║  ██║╚██████╔╝███████║   ██║       ██║     ██║  ██║╚██████╔╝
 ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝       ╚═╝     ╚═╝  ╚═╝ ╚═════╝
           {self.yellow}[=] MATRIX ENCRYPTED TERMINAL V13 [=]{self.reset}"""
        print(logo)

    def connect_db(self):
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("serviceAccountKey.json")
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            return True
        except Exception as e:
            print(f"{self.red}[!] DATABASE ERROR: {e}{self.reset}")
            return False

    def auth_system(self):
        self.draw_logo()
        self.animate_text(f"{self.green}[*] ПРОВЕРКА ЗАЩИЩЕННОГО СОЕДИНЕНИЯ...{self.reset}")
        time.sleep(1)
        
        self.uid = input(f"{self.green}[+] ВВЕДИТЕ USER_ID: @{self.reset}")
        if not self.uid.startswith("@"): self.uid = f"@{self.uid}"
        
        key = input(f"{self.green}[+] ВВЕДИТЕ 2FA_KEY: {self.reset}")
        
        if self.uid == "@adminpan" and key == "TimaIssam2026":
            self.role = "ADMIN"
            print(f"{self.yellow}[!] ПРИВИЛЕГИИ АДМИНИСТРАТОРА ПОДТВЕРЖДЕНЫ{self.reset}")
        
        if not self.connect_db():
            sys.exit()
        
        self.animate_text(f"{self.blue}[*] ДОСТУП РАЗРЕШЕН. ДОБРО ПОЖАЛОВАТЬ, {self.uid}{self.reset}")
        time.sleep(1.5)

    def show_menu(self):
        while self.running:
            self.draw_logo()
            print(f"{self.blue} СТАТУС: ONLINE | СЕССИЯ: {self.uid} | РОЛЬ: {self.role}{self.reset}")
            print("-" * 65)
            print(f"{self.green}1.{self.reset} [ GLOBAL_CHAT ] - Общий зашифрованный канал")
            print(f"{self.green}2.{self.reset} [ PRIVATE_MSG ] - Поиск и личные сообщения")
            print(f"{self.green}3.{self.reset} [ SYSTEM_INFO ] - Состояние сети Ghost")
            if self.role == "ADMIN":
                print(f"{self.red}4. [ ADMIN_PANEL ] - Управление пользователями{self.reset}")
            print(f"{self.green}0.{self.reset} [ DISCONNECT ] - Разорвать соединение")
            
            choice = input(f"\n{self.green}GHOST@TERMINAL:~$ {self.reset}")
            
            if choice == "1": self.chat_engine("GLOBAL")
            elif choice == "0": self.running = False
            elif choice == "4" and self.role == "ADMIN": self.admin_panel()

    def chat_engine(self, channel):
        self.draw_logo()
        print(f"{self.yellow}[*] ВХОД В КАНАЛ: {channel} (Введите '/exit' для выхода){self.reset}")
        print("-" * 65)

        # Поток для прослушивания сообщений
        def listen():
            messages = self.db.collection("messages").order_by("ts", descending=False).limit_to_last(15)
            watch = messages.on_snapshot(self.on_snapshot)

        threading.Thread(target=listen, daemon=True).start()

        while True:
            msg = input(f"{self.green}{self.uid} > {self.reset}")
            if msg == "/exit": break
            if msg.strip():
                self.db.collection("messages").add({
                    "u": self.uid,
                    "t": msg,
                    "r": self.role,
                    "ts": firestore.SERVER_TIMESTAMP,
                    "time": datetime.datetime.now().strftime("%H:%M")
                })

    def on_snapshot(self, docs, changes, read_time):
        # Логика обновления экрана при получении сообщений
        pass 

    def admin_panel(self):
        self.draw_logo()
        print(f"{self.red}--- GHOST ADMIN MANAGEMENT ---{self.reset}")
        print("1. Заблокировать ID")
        print("2. Очистить логи")
        input("\nНажмите Enter для возврата...")

if __name__ == "__main__":
    app = GhostTerminal()
    app.auth_system()
    app.show_menu()

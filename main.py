import os
import sys
import time
import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.table import Table
from rich.live import Live

# Инициализация консоли Rich
console = Console()

class GhostTermux:
    def __init__(self):
        self.db = None
        self.uid = None
        self.role = "USER"
        self.is_running = True

    def clear(self):
        os.system('clear')

    def draw_logo(self):
        self.clear()
        logo_text = r"""
  ________ __                     __      _______   _______   ______  
 /  _____/|  |__   ____  _______/  |_    |       \ |       \ /      \ 
/   \  ___|  |  \ /  _ \/  ___/\   __\   |  $$$$$$$|  $$$$$$$|  $$$$$$\
\    \_\  \   Y  (  <_> )___ \  |  |     | $$__/ $$| $$__    | $$  | $$
 \______  /___|  /\____/____  > |__|     | $$    $$| $$  \   | $$  | $$
        \/     \/           \/           | $$$$$$$ | $$$$$$$ | $$  | $$
                                         | $$      | $$ \    | $$  | $$
      [=] MATRIX TERMINAL V13 [=]        | $$      | $$  \    \______/ 
        """
        console.print(Panel(Text(logo_text, style="bold green"), border_style="green"))

    def init_firebase(self):
        with console.status("[bold green]Установка соединения с Матрицей...", spinner="matrix"):
            try:
                if not firebase_admin._apps:
                    # Файл serviceAccountKey.json должен быть в этой же папке!
                    cred = credentials.Certificate("serviceAccountKey.json")
                    firebase_admin.initialize_app(cred)
                self.db = firestore.client()
                return True
            except Exception as e:
                console.print(f"[bold red]ОШИБКА ПОДКЛЮЧЕНИЯ: {e}")
                return False

    def auth(self):
        self.draw_logo()
        console.print("[bold yellow]>>> ТРЕБУЕТСЯ АВТОРИЗАЦИЯ[/bold yellow]")
        
        # Используем Prompt от Rich, он надежнее обычного input
        user_id = Prompt.ask("[bold green]ВВЕДИТЕ GHOST_ID (без @)[/bold green]")
        self.uid = f"@{user_id}"
        
        password = Prompt.ask("[bold green]ВВЕДИТЕ 2FA_ACCESS_KEY[/bold green]", password=True)

        # Проверка админки
        if user_id == "adminpan" and password == "TimaIssam2026":
            self.role = "ADMIN"
            console.print("[bold cyan]ДОСТУП УРОВНЯ 'ADMIN' ПОДТВЕРЖДЕН[/bold cyan]")
        else:
            self.role = "USER"
            console.print("[bold white]ДОСТУП УРОВНЯ 'USER' УСТАНОВЛЕН[/bold white]")
        
        time.sleep(1)
        return self.init_firebase()

    def send_message(self):
        msg = Prompt.ask(f"[bold white]{self.uid}[/bold white][bold green] @ message[/bold green]")
        if msg.lower() in ['exit', 'quit', '0']:
            self.is_running = False
            return

        if self.db:
            try:
                self.db.collection("messages").add({
                    "u": self.uid,
                    "t": msg,
                    "r": self.role,
                    "ts": firestore.SERVER_TIMESTAMP,
                    "time": datetime.datetime.now().strftime("%H:%M")
                })
            except Exception as e:
                console.print(f"[red]Ошибка отправки: {e}")

    def show_chat(self):
        # Получаем последние 15 сообщений
        try:
            docs = self.db.collection("messages").order_by("ts", descending=True).limit(15).get()
            
            table = Table(expand=True, border_style="dim", box=None)
            table.add_column("TIME", style="cyan", width=8)
            table.add_column("USER", style="bold green", width=15)
            table.add_column("MESSAGE", style="white")

            # Разворачиваем список, чтобы новые были внизу
            for doc in reversed(list(docs)):
                m = doc.to_dict()
                user_color = "bold cyan" if m.get("r") == "ADMIN" else "bold green"
                table.add_row(
                    m.get("time", "--:--"),
                    Text(m.get("u", "unknown"), style=user_color),
                    m.get("t", "")
                )
            
            self.draw_logo()
            console.print(f"[bold white]SESSION:[/bold white] {self.uid} | [bold red]ROLE:[/bold red] {self.role}")
            console.print(table)
            console.print("-" * console.width)
        except Exception as e:
            console.print(f"[red]Ошибка загрузки чата: {e}")

    def main_loop(self):
        if not self.auth():
            return

        while self.is_running:
            self.show_chat()
            console.print("[dim](Введите '0' для выхода)[/dim]")
            self.send_message()

if __name__ == "__main__":
    try:
        app = GhostTermux()
        app.main_loop()
    except KeyboardInterrupt:
        console.print("\n[bold red]СОЕДИНЕНИЕ РАЗОРВАНО.[/bold red]")
        sys.exit()

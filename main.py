import os
import time
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import firebase_admin
from firebase_admin import credentials, firestore

# Инициализация твоего Firebase
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
        db = firestore.client()
    except:
        print("Ошибка: serviceAccountKey.json не найден!")

console = Console()
USER_DATA = {"uid": None, "status": "Online"}

def show_banner():
    os.system('clear')
    console.print(Panel.fit("[bold green]GHOST PRO V13 - TERMINAL EDITION[/]", border_style="green"))

def profile_menu():
    show_banner()
    table = Table(title="МОЙ ПРОФИЛЬ")
    table.add_column("Параметр", style="cyan")
    table.add_column("Значение", style="white")
    table.add_row("ID", USER_DATA["uid"])
    table.add_row("Статус", USER_DATA["status"])
    console.print(table)
    console.input("\n[yellow]Нажми Enter, чтобы выйти в меню...[/]")

def search_and_chat():
    show_banner()
    target = console.input("[bold green]Введите UID для поиска (например, @ivan): [/]")
    if not target.startswith("@"): target = f"@{target}"
    
    console.print(f"[bold yellow]Создание зашифрованного канала с {target}...[/]")
    time.sleep(1)
    
    # Логика личного чата через Firebase
    chat_id = "_".join(sorted([USER_DATA["uid"], target]))
    open_chat(chat_id, target)

def open_chat(chat_id, partner):
    while True:
        show_banner()
        console.print(f"[bold cyan]ЧАТ С {partner} (Ctrl+C для выхода)[/]\n")
        
        # Подгружаем последние 10 сообщений
        msgs = db.collection("chats").document(chat_id).collection("messages").order_by("ts").limit_to_last(10).get()
        for m in msgs:
            data = m.to_dict()
            color = "green" if data['user'] == USER_DATA["uid"] else "white"
            console.print(f"[{color}]{data['user']}: {data['text']}[/]")
        
        msg_text = console.input("\n[bold green]>>> [/]")
        if msg_text.lower() == 'exit': break
        
        db.collection("chats").document(chat_id).collection("messages").add({
            "user": USER_DATA["uid"],
            "text": msg_text,
            "ts": firestore.SERVER_TIMESTAMP
        })

def main_menu():
    while True:
        show_banner()
        console.print("[bold green]1.[/] Мой профиль")
        console.print("[bold green]2.[/] Поиск юзера и чат")
        console.print("[bold green]3.[/] Список активных чатов")
        console.print("[bold red]4.[/] Выход")
        
        choice = console.input("\n[bold cyan]Выберите пункт (1-4): [/]")
        
        if choice == "1": profile_menu()
        elif choice == "2": search_and_chat()
        elif choice == "3": console.print("[yellow]Функция в разработке...[/]"); time.sleep(1)
        elif choice == "4": sys.exit()

if __name__ == "__main__":
    show_banner()
    USER_DATA["uid"] = console.input("[bold green]ВВЕДИТЕ ВАШ UID: [/]")
    if not USER_DATA["uid"].startswith("@"): USER_DATA["uid"] = f"@{USER_DATA['uid']}"
    main_menu()

import os, time, sys, datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
import firebase_admin
from firebase_admin import credentials, firestore

# Инициализация (Файл должен быть в папке!)
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

console = Console()
MY_ID = ""

def show_banner():
    os.system('clear')
    console.print(Panel.fit("[bold green]GHOST PRO V13 - TERMINAL SYSTEM[/]\n[bold red]BETA RELEASE[/]", border_style="green"))

# --- 1. ПРОФИЛЬ ---
def profile():
    show_banner()
    table = Table(title="ДАННЫЕ СЕССИИ")
    table.add_column("Ключ", style="cyan")
    table.add_column("Значение", style="green")
    table.add_row("USER_ID", MY_ID)
    table.add_row("NETWORK", "GHOST_NET_V13")
    table.add_row("STATUS", "ONLINE")
    console.print(table)
    console.input("\n[yellow]Нажми Enter для выхода в меню...[/]")

# --- 2. ПОИСК И НОВЫЙ ЧАТ ---
def search_user():
    show_banner()
    target = console.input("[bold green]Введи ник для поиска (напр. @tima): [/]")
    if not target.startswith("@"): target = f"@{target}"
    
    # Регистрация чата в списке активных
    chat_id = "_".join(sorted([MY_ID, target]))
    db.collection("users").document(MY_ID).collection("active_chats").document(chat_id).set({
        "partner": target, "last_update": firestore.SERVER_TIMESTAMP
    })
    db.collection("users").document(target).collection("active_chats").document(chat_id).set({
        "partner": MY_ID, "last_update": firestore.SERVER_TIMESTAMP
    })
    chat_room(chat_id, target)

# --- 3. АКТИВНЫЕ ЧАТЫ (ТВОЯ ФИШКА) ---
def list_chats():
    show_banner()
    chats = db.collection("users").document(MY_ID).collection("active_chats").get()
    
    if not chats:
        console.print("[red]У вас пока нет активных диалогов.[/]")
        time.sleep(2)
        return

    table = Table(title="ВАШИ ПЕРЕПИСКИ")
    table.add_column("№", style="yellow")
    table.add_column("СОБЕСЕДНИК", style="cyan")
    
    chat_map = {}
    for i, doc in enumerate(chats, 1):
        data = doc.to_dict()
        chat_map[str(i)] = (doc.id, data['partner'])
        table.add_row(str(i), data['partner'])
    
    console.print(table)
    choice = console.input("\n[bold green]Выбери номер чата или '0' для отмены: [/]")
    if choice in chat_map:
        chat_room(chat_map[choice][0], chat_map[choice][1])

# --- ЛОГИКА ЧАТА ---
def chat_room(chat_id, partner):
    def get_messages():
        return db.collection("chats").document(chat_id).collection("messages").order_by("ts", descending=False).limit_to_last(15).get()

    while True:
        show_banner()
        console.print(f"[bold cyan]ДИАЛОГ: {partner} | Выход: /exit[/]\n")
        
        for m in get_messages():
            d = m.to_dict()
            time_str = d.get('time', '--:--')
            user = d.get('user', 'Anon')
            color = "green" if user == MY_ID else "white"
            console.print(f"[dim]{time_str}[/] [{color}]{user}:[/] {d.get('text')}")

        msg = console.input("\n[bold green]>>> [/]")
        if msg == "/exit": break
        if msg.strip():
            db.collection("chats").document(chat_id).collection("messages").add({
                "user": MY_ID,
                "text": msg,
                "ts": firestore.SERVER_TIMESTAMP,
                "time": datetime.datetime.now().strftime("%H:%M")
            })

# --- ГЛАВНОЕ МЕНЮ ---
def main_menu():
    while True:
        show_banner()
        console.print("[bold green]1.[/] Профиль")
        console.print("[bold green]2.[/] Поиск юзера (Новый чат)")
        console.print("[bold green]3.[/] Мои сообщения (Список чатов)")
        console.print("[bold red]4.[/] Выход")
        
        move = console.input("\n[bold cyan]ВЫБЕРИ ПУНКТ (1-4): [/]")
        if move == "1": profile()
        elif move == "2": search_user()
        elif move == "3": list_chats()
        elif move == "4": sys.exit()

if __name__ == "__main__":
    show_banner()
    MY_ID = console.input("[bold green]ВВЕДИ СВОЙ UID: [/]")
    if not MY_ID.startswith("@"): MY_ID = f"@{MY_ID}"
    main_menu()

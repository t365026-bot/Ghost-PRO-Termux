import time
import os
import sys
import datetime
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
import firebase_admin
from firebase_admin import credentials, firestore

# ДАННЫЕ ПРОЕКТА
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"ОШИБКА БАЗЫ: {e}")

console = Console()
chat_history = []
last_msg_count = 0

def play_notification():
    # Простой системный писк (бип) для Termux
    print("\a", end="") 

def generate_ui():
    table = Table(show_header=True, header_style="bold green", expand=True, 
                  title="[bold red]GHOST PRO V13 - PRIVATE TERMINAL[/]")
    table.add_column("TIME", style="dim", width=10)
    table.add_column("SENDER", style="bold cyan", width=15)
    table.add_column("MESSAGE", style="white")

    # Берем последние 15 сообщений для экрана
    for msg in chat_history[-15:]:
        table.add_row(
            msg.get('time', '--:--'),
            msg.get('user', 'Anon'),
            msg.get('text', '')
        )
    
    footer = "[bold yellow]Ctrl+C[/] -> Отправить сообщение | [bold yellow]Exit[/] -> Выход"
    return Panel(table, border_style="green", subtitle=footer)

def sync_messages(docs, changes, read_time):
    global chat_history, last_msg_count
    new_history = [d.to_dict() for d in docs]
    
    # Если сообщений стало больше — значит пришло новое, пищим
    if len(new_history) > last_msg_count and last_msg_count != 0:
        play_notification()
    
    chat_history = new_history
    last_msg_count = len(chat_history)

def main():
    os.system('clear')
    console.print("[bold green]INITIALIZING MATRIX NETWORK...[/]")
    my_uid = console.input("[bold green]ENTER YOUR UID: [/]")
    if not my_uid.startswith("@"): my_uid = f"@{my_uid}"

    # Подписка на коллекцию сообщений в реальном времени
    # Можно менять путь на "private_chats/ID/messages" для лички
    query = db.collection("messages").order_by("ts", descending=False).limit_to_last(30)
    query.on_snapshot(sync_messages)

    try:
        # Режим Live обновляет экран сам каждые полсекунды
        with Live(generate_ui(), refresh_per_second=2, screen=True) as live:
            while True:
                live.update(generate_ui())
                time.sleep(0.5)
    except KeyboardInterrupt:
        # Режим отправки сообщения
        console.print("\n" + "—"*30)
        msg_text = console.input("[bold green]WRITE MESSAGE: [/]")
        
        if msg_text.lower() == 'exit':
            sys.exit()
            
        if msg_text:
            db.collection("messages").add({
                "user": my_uid,
                "text": msg_text,
                "ts": firestore.SERVER_TIMESTAMP,
                "time": datetime.datetime.now().strftime("%H:%M")
            })
        
        # Перезапуск, чтобы вернуться в режим онлайн-просмотра
        os.execv(sys.executable, ['python'] + sys.argv)

if __name__ == "__main__":
    main()

import flet as ft
import datetime
import firebase_admin
from firebase_admin import credentials, firestore, storage

# --- ПОДКЛЮЧЕНИЕ FIREBASE ---
# Используем твой проект ghost-pro-5aa22
try:
    # Файл serviceAccountKey.json должен быть в папке с ботом!
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'storage_bucket': 'ghost-pro-5aa22.firebasestorage.app'
    })
    db = firestore.client()
except Exception as e:
    print(f"Ошибка Firebase: {e}")

def main(page: ft.Page):
    page.title = "GHOST PRO V13: TERMUX SERVER"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    
    state = {"uid": None, "role": "USER"}

    chat_container = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)

    # Слушаем сообщения из Firebase (Real-time)
    def on_snapshot(docs, changes, read_time):
        chat_container.controls.clear()
        for doc in docs:
            m = doc.to_dict()
            chat_container.controls.append(
                ft.Text(f"{m.get('user')}: {m.get('text')}", color="green" if m.get('user') == "@ADMIN_CORE" else "white")
            )
        page.update()

    db.collection("messages").order_by("timestamp").on_snapshot(on_snapshot)

    def send_data(e):
        if msg_input.value:
            db.collection("messages").add({
                "user": state["uid"],
                "text": msg_input.value,
                "timestamp": firestore.SERVER_TIMESTAMP
            })
            msg_input.value = ""
            page.update()

    def login(e):
        if user_in.value == "adminpan" and pass_in.value == "TimaIssam2026":
            state["uid"], state["role"] = "@ADMIN_CORE", "ADMIN"
        else:
            state["uid"] = f"@{user_in.value}"
        
        page.clean()
        page.add(
            ft.Column([
                ft.Text(f"LOGGED AS: {state['uid']}", color="#00FF00", weight="bold"),
                ft.Container(content=chat_container, expand=True, border=ft.border.all(1, "#004400")),
                ft.Row([msg_input, ft.IconButton(ft.icons.SEND, on_click=send_data)])
            ], expand=True)
        )

    user_in = ft.TextField(label="UID")
    pass_in = ft.TextField(label="KEY", password=True)
    msg_input = ft.TextField(hint_text="TYPE...", expand=True)

    page.add(
        ft.Column([
            ft.Text("GHOST_PRO_TERMUX", size=30, color="#00FF00", weight="bold"),
            user_in, pass_in,
            ft.ElevatedButton("CONNECT", on_click=login)
        ], horizontal_alignment="center")
    )

# Запуск именно как веб-сервера для Termux
if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)

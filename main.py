import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore

# АВТО-ПОДКЛЮЧЕНИЕ К ТВОЕЙ СЕТИ
try:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {'storage_bucket': 'ghost-pro-5aa22.firebasestorage.app'})
    db = firestore.client()
except:
    print("ОШИБКА: Файл ключа не найден в папке!")

def main(page: ft.Page):
    page.title = "GHOST PRO V13"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    
    state = {"uid": None, "role": "USER"}
    
    # Элементы интерфейса
    chat_list = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
    users_list = ft.Text("ОНЛАЙН: @Загрузка...", color="#00FF00", size=12)

    def on_message(docs, changes, read_time):
        chat_list.controls.clear()
        active_users = set()
        for doc in docs:
            m = doc.to_dict()
            user = m.get("user", "Unknown")
            active_users.add(user)
            chat_list.controls.append(
                ft.Container(
                    content=ft.Text(f"{user}: {m.get('text')}", color="white"),
                    padding=10, border=ft.border.all(1, "#004400"), border_radius=5
                )
            )
        users_list.value = f"В СЕТИ: {', '.join(list(active_users))}"
        page.update()

    def send(e):
        if msg_in.value:
            db.collection("messages").add({
                "user": state["uid"],
                "text": msg_in.value,
                "timestamp": firestore.SERVER_TIMESTAMP
            })
            msg_in.value = ""
            page.update()

    def login(e):
        if user_in.value:
            state["uid"] = f"@{user_in.value}"
            if user_in.value == "adminpan" and pass_in.value == "TimaIssam2026":
                state["role"] = "ADMIN"
            
            page.clean()
            page.add(
                ft.Column([
                    ft.Row([ft.Text("GHOST_NETWORK", size=20, weight="bold"), users_list], justify="spaceBetween"),
                    ft.Container(content=chat_list, expand=True, border=ft.border.all(1, "#002200")),
                    ft.Row([msg_in, ft.IconButton(ft.icons.SEND, on_click=send)])
                ], expand=True, padding=10)
            )
            # Слушаем твою базу ghost-pro-5aa22
            db.collection("messages").order_by("timestamp").on_snapshot(on_message)

    user_in = ft.TextField(label="ТВОЙ НИК", border_color="#00FF00")
    pass_in = ft.TextField(label="ПАРОЛЬ", password=True, border_color="#00FF00")
    msg_in = ft.TextField(hint_text="Сообщение...", expand=True)

    page.add(
        ft.Column([
            ft.Text("GHOST_PRO_CORE", size=30, color="#00FF00", weight="bold"),
            user_in, pass_in,
            ft.ElevatedButton("ВОЙТИ В СЕТЬ", on_click=login)
        ], horizontal_alignment="center")
    )

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)

import flet as ft
import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# --- ПОДКЛЮЧЕНИЕ FIREBASE ---
# Файл serviceAccountKey.json должен лежать в той же папке!
try:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'ghost-pro-5aa22.firebasestorage.app'
    })
    db = firestore.client()
except Exception as e:
    print(f"[-] Ошибка конфига: {e}")

def main(page: ft.Page):
    page.title = "GHOST PRO V13"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    
    state = {"uid": None, "role": "USER"}
    chat_container = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)

    # Исправленный обработчик (совместим с новыми версиями flet)
    def on_file_res(e):
        if e.files:
            page.show_snack_bar(ft.SnackBar(ft.Text(f"Выбрано: {e.files[0].name}")))

    picker = ft.FilePicker(on_result=on_file_res)
    page.overlay.append(picker)

    def send_msg(e):
        if msg_in.value:
            db.collection("messages").add({
                "user": state["uid"],
                "text": msg_in.value,
                "timestamp": firestore.SERVER_TIMESTAMP
            })
            msg_in.value = ""
            page.update()

    def login_go(e):
        if user_in.value == "adminpan" and pass_in.value == "TimaIssam2026":
            state["uid"], state["role"] = "@ADMIN_CORE", "ADMIN"
        else:
            state["uid"] = f"@{user_in.value}"
        
        page.clean()
        page.add(
            ft.Column([
                ft.Row([
                    ft.Text(f"SESSION: {state['uid']}", color="#00FF00", weight="bold"),
                    ft.IconButton(ft.icons.DELETE_FOREVER, icon_color="red", visible=state["role"]=="ADMIN")
                ], justify="spaceBetween"),
                ft.Container(content=chat_container, expand=True, border=ft.border.all(1, "#004400"), padding=10),
                ft.Row([
                    ft.IconButton(ft.icons.ADD_A_PHOTO, on_click=lambda _: picker.pick_files()),
                    msg_in, 
                    ft.IconButton(ft.icons.SEND, on_click=send_msg)
                ])
            ], expand=True)
        )
        # Real-time прослушка сообщений
        db.collection("messages").order_by("timestamp").on_snapshot(lambda docs, c, t: (
            chat_container.controls.clear(),
            [chat_container.controls.append(ft.Text(f"{d.to_dict().get('user')}: {d.to_dict().get('text')}", color="white")) for d in docs],
            page.update()
        ))

    user_in = ft.TextField(label="UID / EMAIL", border_color="#00FF00")
    pass_in = ft.TextField(label="KEY", password=True, border_color="#00FF00")
    msg_in = ft.TextField(hint_text="Сообщение...", expand=True, border_color="#00FF00")

    page.add(
        ft.Column([
            ft.Text("GHOST_PRO_CORE", size=30, color="#00FF00", weight="bold"),
            user_in, pass_in,
            ft.ElevatedButton("CONNECT", on_click=login_go, bgcolor="#002200", color="#00FF00")
        ], horizontal_alignment="center")
    )

if __name__ == "__main__":
    # Выводим ссылку в консоль Termux перед запуском
    print("\n" + "="*30)
    print("GHOST SERVER ACTIVE")
    print("URL: http://127.0.0.1:8550")
    print("="*30 + "\n")
    
    # Запуск веб-версии для работы в браузере телефона
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)

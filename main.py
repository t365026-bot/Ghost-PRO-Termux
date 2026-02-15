import flet as ft
import datetime
import base64
import sys

# ASCII ART для хакерского стиля в терминале
def print_banner():
    banner = """
    \033[1;32m
     _____ _   _  _____ _____ _____   ___________ _____ 
    |  __ \ | | ||  _  /  ___|_   _| | ___ \ ___ \  _  |
    | |  \/ |_| || | | \ `--.  | |   | |_/ / |_/ / | | |
    | | __|  _  || | | |`--. \ | |   |  __/|  _  / | | |
    | |_\ \ | | |\ \_/ /\__/ / | |   | |   | | \ \ \_/ /
     \____\_| |_/ \___/\____/  \_/   \_|   \_|  \_\___/ 
           [=] MATRIX ENCRYPTED NETWORK V13 [=]
    \033[0m
    """
    print(banner)

def main(page: ft.Page):
    page.title = "GHOST PRO V13"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.padding = 10
    
    state = {
        "uid": "@guest",
        "role": "USER",
        "users_db": ["@ADMIN_CORE", "@root", "@ghost", "@anon"]
    }

    # ПИКЕР ФАЙЛОВ (РЕАЛЬНАЯ ПЕРЕДАЧА)
    def on_file_result(e: ft.FilePickerResultEvent):
        if e.files:
            for f in e.files:
                with open(f.path, "rb") as file_raw:
                    b64_data = base64.b64encode(file_raw.read()).decode()
                
                ext = f.name.split(".")[-1].lower()
                m_type = "image" if ext in ["jpg", "png", "jpeg"] else "video" if ext in ["mp4"] else "audio" if ext in ["mp3", "wav"] else "file"

                page.pubsub.send_all(str({
                    "user": state["uid"],
                    "type": m_type,
                    "name": f.name,
                    "data": b64_data,
                    "time": datetime.datetime.now().strftime("%H:%M")
                }))

    file_picker = ft.FilePicker(on_result=on_file_result)
    page.overlay.append(file_picker)

    # ОБРАБОТКА СООБЩЕНИЙ
    def on_broadcast(msg_str):
        data = eval(msg_str)
        is_me = data["user"] == state["uid"]
        
        content = ft.Column(spacing=5)
        content.controls.append(ft.Text(data["user"], size=10, color="#00FF00", weight="bold"))
        
        if data["type"] == "text":
            content.controls.append(ft.Text(data["text"], color="white", size=16))
        elif data["type"] == "image":
            content.controls.append(ft.Image(src_base64=data["data"], width=300, border_radius=10))
        elif data["type"] in ["video", "audio", "file"]:
            content.controls.append(ft.Row([ft.Icon(ft.icons.ATTACH_FILE, color="#00FF00"), ft.Text(data["name"], color="white")]))

        chat_list.controls.append(
            ft.Container(
                content=content, padding=12, bgcolor="#0A0A0A",
                border=ft.border.all(1, "#00FF00" if is_me else "#004400"),
                border_radius=10, margin=ft.margin.only(bottom=10)
            )
        )
        page.update()

    page.pubsub.subscribe(on_broadcast)

    chat_list = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
    msg_input = ft.TextField(hint_text=">>> ENTER_PAYLOAD", expand=True, border_color="#00FF00", color="#00FF00")

    def send_msg(e):
        if msg_input.value:
            page.pubsub.send_all(str({
                "user": state["uid"], "type": "text", 
                "text": msg_input.value, "time": datetime.datetime.now().strftime("%H:%M")
            }))
            msg_input.value = ""
            page.update()

    # ИНТЕРФЕЙС ГЛАВНОГО ЭКРАНА
    def show_main():
        page.clean()
        page.add(
            ft.Column([
                ft.Row([
                    ft.Text("GHOST_NET", color="#00FF00", weight="bold", size=22),
                    ft.Row([
                        ft.IconButton(ft.icons.ADMIN_PANEL_SETTINGS, icon_color="red", visible=state["role"]=="ADMIN", on_click=lambda _: show_admin()),
                        ft.IconButton(ft.icons.PERSON, icon_color="#00FF00", on_click=lambda _: show_profile())
                    ])
                ], justify="spaceBetween"),
                ft.TextField(hint_text="SEARCH_UID...", prefix_icon=ft.icons.SEARCH, height=40, border_color="#003300", on_submit=lambda e: page.show_snack_bar(ft.SnackBar(ft.Text("Searching...")))),
                ft.Container(content=chat_list, expand=True, border=ft.border.all(1, "#002200"), padding=10),
                ft.Row([
                    ft.IconButton(ft.icons.ATTACH_FILE, icon_color="#00FF00", on_click=lambda _: file_picker.pick_files()),
                    msg_input,
                    ft.IconButton(ft.icons.SEND, icon_color="#00FF00", on_click=send_msg)
                ])
            ], expand=True)
        )

    def show_admin():
        page.clean()
        page.add(ft.Column([ft.Text("ADMIN_CORE", color="red", size=30), ft.ElevatedButton("BAN_ALL", bgcolor="red", color="white"), ft.ElevatedButton("BACK", on_click=lambda _: show_main())], horizontal_alignment="center"))

    def show_profile():
        page.clean()
        page.add(ft.Column([ft.CircleAvatar(radius=50, bgcolor="#002200"), ft.Text(state["uid"], size=25, color="#00FF00"), ft.ElevatedButton("BACK", on_click=lambda _: show_main())], horizontal_alignment="center"))

    # ВХОД
    def login(e):
        if login_in.value == "adminpan" and pass_in.value == "TimaIssam2026":
            state["role"], state["uid"] = "ADMIN", "@ADMIN_CORE"
        else: state["uid"] = f"@{login_in.value}"
        show_main()

    login_in = ft.TextField(label="UID")
    pass_in = ft.TextField(label="KEY", password=True)
    page.add(ft.Column([ft.Text("GHOST_PRO", size=40, color="#00FF00", weight="bold"), login_in, pass_in, ft.ElevatedButton("INIT_SESSION", on_click=login, width=300)], horizontal_alignment="center"))

if __name__ == "__main__":
    print_banner()
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)

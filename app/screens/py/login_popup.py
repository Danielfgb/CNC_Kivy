from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFlatButton
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDRoundFlatIconButton
from kivymd.app import MDApp
from kivy.lang import Builder
import json



KV = '''
<Content>:
    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    height: "150dp"

    MDLabel:
        id: login_message
        text: ""
        halign: "center"
        color: [1, 0, 0, 0] 
'''

class Content(BoxLayout):
    pass

class LoginPopup:
    dialog = None
    error_dialog = None

    def __init__(self):
        Builder.load_string(KV)
        self.dialog = MDDialog(
            title="Login",
            type="custom",
            content_cls=Content(),
            buttons=[
                MDRoundFlatIconButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=[1, 0, 0, 1],
                    on_release=self.close_dialog,
                ),
                MDRoundFlatIconButton(
                    text="LOGIN",
                    theme_text_color="Custom",
                    text_color=[0, 0, 0, 1],
                    on_release=lambda x: self.authenticate(
                        self.dialog.content_cls.ids.username.text,
                        self.dialog.content_cls.ids.password.text
                    ),
                ),
            ],
        )

    def show(self):
        self.dialog.open()

    def close_dialog(self, instance):
        self.dialog.dismiss()

    def authenticate(self, username, password):
        print("Username:", username)
        print("Password:", password)

        try:
            with open('./app/resources/data/credentials.json', 'r') as f:
                data = json.load(f)

                if username == data.get("username") and password == data.get("password"):
                    print("Login exitoso")
                    self.dialog.dismiss()
                    app = MDApp.get_running_app()
                    app.root.current = 'calibrar'
                else:
                    print("Credenciales incorrectas")
                    self.dialog.content_cls.ids.username.text = ""
                    self.dialog.content_cls.ids.password.text = ""
                    self.show_error_dialog("Credenciales incorrectas")
        except FileNotFoundError:
            print("Archivo de credenciales no encontrado")
            self.dialog.content_cls.ids.username.text = ""
            self.dialog.content_cls.ids.password.text = ""
            self.show_error_dialog("Archivo de credenciales no encontrado")

    def show_error_dialog(self, message):
        if not self.error_dialog:
            self.error_dialog = MDDialog(
                title="Error",
                text=message,
                buttons=[
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=[0, 0, 1, 1],
                        on_release=self.close_error_dialog,
                    ),
                ],
            )
        else:
            self.error_dialog.text = message
        self.error_dialog.open()

    def close_error_dialog(self, instance):
        self.error_dialog.dismiss()

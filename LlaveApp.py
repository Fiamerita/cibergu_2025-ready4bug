# LlaveApp.py
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivy.uix.screenmanager import FadeTransition
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.lang import Builder
import requests, threading, base64
from io import BytesIO
from kivy.core.image import Image as CoreImage


class SplashScreen(MDScreen):
    def on_enter(self):
        Clock.schedule_once(self.ir_a_login, 3)

    def ir_a_login(self, *args):
        self.manager.transition.direction = 'left'
        self.manager.current = "login"


class LoginScreen(MDScreen):
    def on_pre_enter(self):
        try:
            self.ids.msg.text = ""
            self.ids.usuario.text = ""
            self.ids.contraseña.text = ""
        except Exception as e:
            print(f"Error al limpiar campos en on_pre_enter: {e}")

    def login(self):
        u = self.ids.usuario.text.strip()
        p = self.ids.contraseña.text.strip()

        if not u or not p:
            self.ids.msg.text = "Usuario y contraseña requeridos"
            return

        def enviar():
            try:
                r = requests.post(
                    "http://localhost:5000/inicio_sesion",
                    json={"usuario": u, "contraseña": p},
                    timeout=5
                )
                data = r.json()
                if data.get("exito"):
                    Clock.schedule_once(lambda dt: self.obtener_qr(), 0)
                else:
                    mensaje = data.get("mensaje", "Credenciales incorrectas")
                    Clock.schedule_once(lambda dt: setattr(self.ids.msg, 'text', mensaje), 0)
            except Exception as e:
                print(f"Error en login: {e}")
                Clock.schedule_once(lambda dt: setattr(self.ids.msg, 'text', "Error de conexión"), 0)

        threading.Thread(target=enviar, daemon=True).start()

    def obtener_qr(self):
        def solicitar():
            try:
                r = requests.get("http://localhost:5000/generar_qr", timeout=5)
                data = r.json()
                b64 = data.get("qr_base64")
                if b64:
                    img = BytesIO(base64.b64decode(b64))
                    core_img = CoreImage(img, ext='png')
                    Clock.schedule_once(lambda dt: self.mostrar_qr(core_img.texture), 0)
            except:
                Clock.schedule_once(lambda dt: setattr(self.ids.msg, 'text', "Error al generar QR"), 0)

        threading.Thread(target=solicitar, daemon=True).start()

    def mostrar_qr(self, texture):
        self.manager.transition.direction = 'left'
        self.manager.current = "qr"
        self.manager.get_screen("qr").mostrar_imagen(texture)


class QRScreen(MDScreen):
    def mostrar_imagen(self, texture):
        self.ids.qr.texture = texture

    def volver_login(self):
        self.manager.transition.direction = 'right'
        self.manager.current = "login"


class LlaveApp(MDApp):
    def build(self):
        Builder.load_file("llavedeacceso.kv")  # 👈 Carga manual del .kv
        sm = MDScreenManager(transition=FadeTransition(duration=0.4))
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(QRScreen(name="qr"))
        sm.current = "splash"
        return sm


if __name__ == '__main__':
    LlaveApp().run()
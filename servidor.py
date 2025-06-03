# LlaveApp.py
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.core.image import Image as CoreImage
import qrcode
import time
import io
import socket
import requests

class LoginScreen(Screen):
    def iniciar_sesion(self):
        u = self.ids.usuario.text.strip()
        p = self.ids.contrasena.text.strip()
        if not u or not p:
            self.ids.msg.text = "[color=ff0000]Usuario y contraseña requeridos[/color]"
            return

        def enviar():
            try:
                ip = self.obtener_ip()
                url = f"https://{ip}:5000/generar_token"
                r = requests.post(url, json={"usuario": u, "contrasena": p}, verify=False)
                if r.status_code == 200:
                    data = r.json()
                    self.manager.get_screen("qr").inicializar_qr(data["token"], ip)
                    self.manager.current = "qr"
                else:
                    self.ids.msg.text = f"[color=ff0000]{r.json().get('error', 'Error de autenticación')}[/color]"
            except Exception as e:
                self.ids.msg.text = f"[color=ff0000]Error: {e}[/color]"

        from threading import Thread
        Thread(target=enviar, daemon=True).start()

    def obtener_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            return s.getsockname()[0]
        except:
            return '127.0.0.1'
        finally:
            s.close()

class QRScreen(Screen):
    def inicializar_qr(self, token, ip):
        self.token_actual = token
        self.ip = ip
        self.contador = 30
        self.mostrar_qr()
        self.ids.timer_label.text = f"Te quedan: {self.contador} segundos"
        self.evento_contador = Clock.schedule_interval(self.actualizar_contador, 1)

    def mostrar_qr(self):
        url_qr = f"https://{self.ip}:5000/validar_token?token={self.token_actual}"
        img = qrcode.make(url_qr)
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        self.ids.qr_image.texture = CoreImage(buffer, ext='png').texture

    def actualizar_contador(self, dt):
        self.contador -= 1
        if self.contador <= 0:
            Clock.unschedule(self.evento_contador)
            self.ids.timer_label.text = "Token caducado"
        else:
            self.ids.timer_label.text = f"Te quedan: {self.contador} segundos"

class LlaveDeAccesoApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(QRScreen(name="qr"))
        return sm

if __name__ == '__main__':
    LlaveDeAccesoApp().run()

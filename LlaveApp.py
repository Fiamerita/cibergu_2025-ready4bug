from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.clock import Clock
import requests
import threading
import time
import webbrowser

import os

class PantallaRegistro(Screen):
    def registrar(self):
        u = self.ids.usuario.text.strip()
        p = self.ids.contraseña.text.strip()
        e = self.ids.email.text.strip()

        if not u or not p or not e:
            self.mostrar("Todos los campos son obligatorios", False)
            return

        def enviar():
            try:
                r = requests.post(
                    "http://localhost:5000/registro",
                    json={"usuario": u, "contraseña": p, "email": e},
                    timeout=5
                )
                resp = r.json()
                Clock.schedule_once(lambda dt: self.mostrar(resp.get("mensaje", "Error"), resp.get("exito", False)), 0)
            except Exception:
                Clock.schedule_once(lambda dt: self.mostrar("Error de conexión", False), 0)

        threading.Thread(target=enviar, daemon=True).start()

    def mostrar(self, msg, exito):
        color = "00aa00" if exito else "ff0000"
        self.ids.msg.text = f"[color={color}]{msg}[/color]"

class PantallaLogin(Screen):
    def iniciar_sesion(self):
        u = self.ids.login_usuario.text.strip()
        p = self.ids.login_contraseña.text.strip()

        if not u or not p:
            self.mostrar("Usuario y contraseña requeridos")
            return

        def enviar():
            try:
                r = requests.post(
                    "http://localhost:5000/inicio_sesion",
                    json={"usuario": u, "contraseña": p},
                    timeout=5
                )
                resp = r.json()
                if resp.get("exito"):
                    Clock.schedule_once(lambda dt: self.generar_qr(), 0)
                else:
                    Clock.schedule_once(lambda dt: self.mostrar(resp.get("mensaje", "Error")), 0)
            except Exception:
                Clock.schedule_once(lambda dt: self.mostrar("Error de conexión"), 0)

        threading.Thread(target=enviar, daemon=True).start()

    def generar_qr(self):
        self._activo = True
        self.ids.layout.clear_widgets()
        self.ids.layout.add_widget(Label(text="Generando código QR...", font_size=24))

        def obtener_qr():
            try:
                r = requests.get('http://localhost:5000/generar_qr', timeout=5)
                data = r.json()
                self.token = data.get('token')
                if self.token:
                    Clock.schedule_once(lambda dt: self.mostrar_qr(), 0)
                    threading.Thread(target=self.verificar_token, daemon=True).start()
                else:
                    Clock.schedule_once(lambda dt: self.mostrar_error("No se pudo obtener el token"), 0)
            except Exception:
                Clock.schedule_once(lambda dt: self.mostrar_error("Error: no se conecta al servidor"), 0)

        threading.Thread(target=obtener_qr, daemon=True).start()

    def mostrar_qr(self):
        self.ids.layout.clear_widgets()
        self.ids.layout.add_widget(Image(source='qr_token.png'))

    def mostrar_error(self, msg):
        self.ids.layout.clear_widgets()
        self.ids.layout.add_widget(Label(text=msg, color=(1, 0, 0, 1), font_size=20))

    def verificar_token(self):
        while getattr(self, "_activo", False):
            try:
                r = requests.get(f'http://localhost:5000/estado_token/{self.token}', timeout=5)
                estado = r.json().get('acceso')
                if estado == 'concedido':
                    self._activo = False
                    Clock.schedule_once(lambda dt: self.abrir_url("acceso_concedido"), 0)
                    break
                elif estado == 'denegado':
                    self._activo = False
                    Clock.schedule_once(lambda dt: self.abrir_url("acceso_denegado"), 0)
                    break
            except Exception:
                pass
            time.sleep(2)

    def abrir_url(self, estado):
        if estado == "acceso_concedido":
            webbrowser.open("https://www.ceeiguadalajara.es/landing/cibergu-2025")
            Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'exito'), 0)
        else:
            webbrowser.open("https://ellibrodepython.com/")
            Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'login'), 0)

    def on_leave(self):
        self._activo = False

    def mostrar(self, msg):
        self.ids.login_msg.text = f"[color=ff0000]{msg}[/color]"

class PantallaExito(Screen):
    pass

class LlaveDeAccesoApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(PantallaLogin(name='login'))
        sm.add_widget(PantallaRegistro(name='registro'))
        sm.add_widget(PantallaExito(name='exito'))
        return sm

if __name__ == '__main__':
    LlaveDeAccesoApp().run()

from kivy.app import App  # Importa la clase base de aplicaciones Kivy
from kivy.uix.screenmanager import ScreenManager, Screen  # Para gestionar pantallas
from kivy.uix.image import Image  # Para mostrar imágenes (como el QR)
from kivy.uix.label import Label  # Para mostrar textos
from kivy.clock import Clock  # Para programar tareas en el hilo principal de Kivy
import requests  # Para hacer peticiones HTTP al servidor Flask
import threading  # Para ejecutar tareas en segundo plano
import time  # Para pausas y temporizadores
import webbrowser  # Para abrir URLs en el navegador
import os  # Para operaciones del sistema (no siempre necesario, pero útil)

class PantallaRegistro(Screen):
    def registrar(self):
        u = self.ids.usuario.text.strip()  # Obtiene el texto del campo usuario
        p = self.ids.contraseña.text.strip()  # Obtiene el texto del campo contraseña
        e = self.ids.email.text.strip()  # Obtiene el texto del campo email

        if not u or not p or not e:  # Si algún campo está vacío
            self.mostrar("Todos los campos son obligatorios", False)
            return

        def enviar():
            try:
                r = requests.post(
                    "http://localhost:5000/registro",  # URL del endpoint de registro
                    json={"usuario": u, "contraseña": p, "email": e},  # Datos a enviar
                    timeout=5  # Tiempo máximo de espera
                )
                resp = r.json()  # Respuesta del servidor en formato JSON
                # Muestra el mensaje recibido en la interfaz
                Clock.schedule_once(lambda dt: self.mostrar(resp.get("mensaje", "Error"), resp.get("exito", False)), 0)
            except Exception:
                # Si hay error de conexión, muestra mensaje de error
                Clock.schedule_once(lambda dt: self.mostrar("Error de conexión", False), 0)

        threading.Thread(target=enviar, daemon=True).start()  # Ejecuta el envío en un hilo aparte

    def mostrar(self, msg, exito):
        color = "00aa00" if exito else "ff0000"  # Verde si éxito, rojo si error
        self.ids.msg.text = f"[color={color}]{msg}[/color]"  # Muestra el mensaje en el label

class PantallaLogin(Screen):
    def iniciar_sesion(self):
        u = self.ids.login_usuario.text.strip()  # Obtiene el usuario
        p = self.ids.login_contraseña.text.strip()  # Obtiene la contraseña

        if not u or not p:  # Si falta usuario o contraseña
            self.mostrar("Usuario y contraseña requeridos")
            return

        def enviar():
            try:
                r = requests.post(
                    "http://localhost:5000/inicio_sesion",  # URL del endpoint de login
                    json={"usuario": u, "contraseña": p},  # Datos a enviar
                    timeout=5
                )
                resp = r.json()
                if resp.get("exito"):
                    # Si el login es exitoso, genera el QR
                    Clock.schedule_once(lambda dt: self.generar_qr(), 0)
                else:
                    # Si falla, muestra el mensaje de error
                    Clock.schedule_once(lambda dt: self.mostrar(resp.get("mensaje", "Error")), 0)
            except Exception:
                # Si hay error de conexión, muestra mensaje de error
                Clock.schedule_once(lambda dt: self.mostrar("Error de conexión"), 0)

        threading.Thread(target=enviar, daemon=True).start()  # Ejecuta el envío en un hilo aparte

    def generar_qr(self):
        self._activo = True  # Marca que está esperando el QR
        self.ids.layout.clear_widgets()  # Limpia el layout
        self.ids.layout.add_widget(Label(text="Generando código QR...", font_size=24))  # Muestra mensaje de espera

        def obtener_qr():
            try:
                r = requests.get('http://localhost:5000/generar_qr', timeout=5)  # Pide el QR al servidor
                data = r.json()
                self.token = data.get('token')  # Guarda el token recibido
                if self.token:
                    # Si hay token, muestra el QR y comienza a verificar el estado
                    Clock.schedule_once(lambda dt: self.mostrar_qr(), 0)
                    threading.Thread(target=self.verificar_token, daemon=True).start()
                else:
                    # Si no hay token, muestra error
                    Clock.schedule_once(lambda dt: self.mostrar_error("No se pudo obtener el token"), 0)
            except Exception:
                # Si hay error de conexión, muestra error
                Clock.schedule_once(lambda dt: self.mostrar_error("Error: no se conecta al servidor"), 0)

        threading.Thread(target=obtener_qr, daemon=True).start()  # Ejecuta la obtención en un hilo aparte

    def mostrar_qr(self):
        self.ids.layout.clear_widgets()  # Limpia el layout
        self.ids.layout.add_widget(Image(source='qr_token.png'))  # Muestra la imagen del QR

    def mostrar_error(self, msg):
        self.ids.layout.clear_widgets()  # Limpia el layout
        self.ids.layout.add_widget(Label(text=msg, color=(1, 0, 0, 1), font_size=20))  # Muestra el error

    def verificar_token(self):
        while getattr(self, "_activo", False):  # Mientras esté esperando
            try:
                r = requests.get(f'http://localhost:5000/estado_token/{self.token}', timeout=5)  # Consulta el estado del token
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
            time.sleep(2)  # Espera 2 segundos antes de volver a consultar

    def abrir_url(self, estado):
        if estado == "acceso_concedido":
            webbrowser.open("https://www.google.es")  # Abre Google si el acceso es concedido
            Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'exito'), 0)  # Cambia a pantalla de éxito
        else:
            webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")  # Abre YouTube si es denegado
            Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'login'), 0)  # Vuelve al login

    def on_leave(self):
        self._activo = False  # Detiene la verificación del token al salir de la pantalla

    def mostrar(self, msg):
        self.ids.login_msg.text = f"[color=ff0000]{msg}[/color]"  # Muestra mensaje de error en el login

class PantallaExito(Screen):
    pass  # Pantalla vacía, solo muestra el mensaje de éxito

class LlaveDeAccesoApp(App):
    def build(self):
        sm = ScreenManager()  # Crea el gestor de pantallas
        sm.add_widget(PantallaLogin(name='login'))  # Añade la pantalla de login
        sm.add_widget(PantallaRegistro(name='registro'))  # Añade la pantalla de registro
        sm.add_widget(PantallaExito(name='exito'))  # Añade la pantalla de éxito
        return sm  # Devuelve el gestor de pantallas

if __name__ == '__main__':
    LlaveDeAccesoApp().run()  # Inicia la aplicación Kivy
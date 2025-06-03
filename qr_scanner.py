import cv2
import numpy as np
from pyzbar.pyzbar import decode
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout


class QRScanner(Image):
    def __init__(self, **kwargs):
        super(QRScanner, self).__init__(**kwargs)
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0 / 30)

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            # Leer el código QR
            decoded_objs = decode(frame)
            for obj in decoded_objs:
                print("QR detectado:", obj.data.decode("utf-8"))

            # Mostrar el frame en la app
            buf = cv2.flip(frame, 0).tostring()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.texture = texture


class MainApp(App):
    def build(self):
        layout = BoxLayout()
        self.qr_view = QRScanner()
        layout.add_widget(self.qr_view)
        return layout


if __name__ == '__main__':
    MainApp().run()
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout


class QRScanner(Image):
    def __init__(self, **kwargs):
        super(QRScanner, self).__init__(**kwargs)
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0 / 30)

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            # Leer el código QR
            decoded_objs = decode(frame)
            for obj in decoded_objs:
                print("QR detectado:", obj.data.decode("utf-8"))

            # Mostrar el frame en la app
            buf = cv2.flip(frame, 0).tostring()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.texture = texture


class MainApp(App):
    def build(self):
        layout = BoxLayout()
        self.qr_view = QRScanner()
        layout.add_widget(self.qr_view)
        return layout


if __name__ == '__main__':
    MainApp().run()

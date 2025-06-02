# 🔐 Llave de Acceso QR

Una aplicación construida con *Kivy* y *Flask* que genera un código QR de acceso único, valida el token en el servidor y confirma la autenticación mediante una interfaz gráfica de usuario.

---

## 📌 Descripción general

Este proyecto simula un sistema de autenticación mediante código QR. Incluye:

- Aplicación de escritorio (cliente) con interfaz en Kivy.
- Servidor web con Flask que genera tokens únicos y los valida.
- Verificación periódica del token hasta recibir autorización.

---

## 🧩 Tecnologías utilizadas

- 🐍 Python 3.10+
- 🔧 Kivy (interfaz de usuario)
- 🌐 Flask (servidor REST)
- 📦 Requests
- 📷 qrcode
- 🔗 threading, socket, webbrowser

---

## 🚀 Cómo ejecutar el proyecto

### 1. Clona el repositorio
```bash
git clone https://github.com/tu-usuario/llave-de-acceso-qr.git
cd llave-de-acceso-qr

from flask import Flask, request, jsonify
import uuid
import qrcode
import os
import json
import socket
from io import BytesIO
import base64

app = Flask(__name__)

TOKENS_VALIDOS = set()
TOKENS_USADOS = set()
USUARIOS_FILE = "usuarios.json"


def cargar_usuarios():
    if not os.path.exists(USUARIOS_FILE):
        return []
    with open(USUARIOS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_usuarios(usuarios):
    with open(USUARIOS_FILE, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, indent=4, ensure_ascii=False)


@app.route('/registro', methods=['POST'])
def registro():
    datos = request.json
    usuario = datos.get("usuario")
    contraseña = datos.get("contraseña")
    email = datos.get("email")

    if not usuario or not contraseña or not email:
        return jsonify({"exito": False, "mensaje": "Faltan datos"}), 400

    usuarios = cargar_usuarios()
    if any(u.get("usuario") == usuario for u in usuarios):
        return jsonify({"exito": False, "mensaje": "Usuario ya existe"}), 409

    usuarios.append({"usuario": usuario, "contraseña": contraseña, "email": email})
    guardar_usuarios(usuarios)

    return jsonify({"exito": True, "mensaje": "Registro exitoso"})


@app.route('/inicio_sesion', methods=['POST'])
def iniciar_sesion():
    datos = request.get_json(force=True)
    usuario = datos.get("usuario")
    contraseña = datos.get("contraseña")
    print(f"Usuario recibido: '{usuario}'")
    print(f"Contraseña recibida: '{contraseña}'")

    if not usuario or not contraseña:
        return jsonify({"exito": False, "mensaje": "Faltan credenciales"}), 400

    usuarios = cargar_usuarios()
    print(f"Usuarios en base: {usuarios}")
    for u in usuarios:
        print(f"Comparando con: {u}")
        if u.get("usuario") == usuario and u.get("contraseña") == contraseña:
            return jsonify({"exito": True, "mensaje": "Inicio de sesión exitoso"})
    return jsonify({"exito": False, "mensaje": "Usuario o contraseña incorrectos"}), 401


def obtener_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


@app.route('/generar_qr')
def generar_qr():
    token = str(uuid.uuid4())
    TOKENS_VALIDOS.add(token)
    url = f"http://{obtener_ip()}:5000/?token={token}"
    img = qrcode.make(url)

    buf = BytesIO()
    img.save(buf, format="PNG")
    img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    return jsonify({"token": token, "url": url, "qr_base64": img_b64})


@app.route('/')
def procesar_token():
    token = request.args.get('token')
    if not token:
        return "Token no proporcionado."
    if token in TOKENS_VALIDOS:
        TOKENS_VALIDOS.remove(token)
        TOKENS_USADOS.add(token)
        return "Token válido. Autenticación confirmada. Puedes cerrar esta pestaña."
    else:
        return "Token inválido o ya usado."


@app.route('/estado_token/<token>')
def estado_token(token):
    if token in TOKENS_VALIDOS:
        return jsonify({"acceso": "pendiente"})
    elif token in TOKENS_USADOS:
        return jsonify({"acceso": "concedido"})
    else:
        return jsonify({"acceso": "denegado"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

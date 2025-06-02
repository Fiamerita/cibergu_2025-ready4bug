from flask import Flask, request, jsonify
import uuid
import qrcode
import os
import json
import socket

app = Flask(__name__)

TOKENS_VALIDOS = set()
TOKENS_USADOS = set()
USUARIOS_FILE = "usuarios.json"

def cargar_usuarios():
    if not os.path.exists(USUARIOS_FILE):
        return []
    with open(USUARIOS_FILE, "r") as f:
        return json.load(f)

def guardar_usuarios(usuarios):
    with open(USUARIOS_FILE, "w") as f:
        json.dump(usuarios, f, indent=4)

@app.route('/registro', methods=['POST'])
def registro():
    datos = request.json
    usuario = datos.get("usuario")
    contraseña = datos.get("contraseña")
    email = datos.get("email")

    if not usuario or not contraseña or not email:
        return jsonify({"exito": False, "mensaje": "Faltan datos"}), 400

    usuarios = cargar_usuarios()
    if any(u["usuario"] == usuario for u in usuarios):
        return jsonify({"exito": False, "mensaje": "Usuario ya existe"}), 409

    usuarios.append({"usuario": usuario, "contraseña": contraseña, "email": email})
    guardar_usuarios(usuarios)

    return jsonify({"exito": True, "mensaje": "Registro exitoso"})

@app.route('/inicio_sesion', methods=['POST'])
def iniciar_sesion():
    datos = request.json
    usuario = datos.get("usuario")
    contraseña = datos.get("contraseña")

    usuarios = cargar_usuarios()
    for u in usuarios:
        if u["usuario"] == usuario and u["contraseña"] == contraseña:
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
    qrcode.make(url).save("qr_token.png")
    return jsonify({"token": token, "url": url})

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

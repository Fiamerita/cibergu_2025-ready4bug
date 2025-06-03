from flask import Flask, request, jsonify  # Importa Flask y utilidades para manejar peticiones y respuestas JSON
import uuid        # Para generar identificadores únicos (tokens)
import qrcode      # Para generar códigos QR
import os          # Para operaciones con archivos y sistema operativo
import json        # Para leer y escribir archivos JSON
import socket      # Para obtener la IP local

app = Flask(__name__)  # Crea la aplicación Flask

TOKENS_VALIDOS = set()    # Conjunto para almacenar tokens válidos (pendientes de usar)
TOKENS_USADOS = set()     # Conjunto para almacenar tokens ya usados
USUARIOS_FILE = "usuarios.json"  # Nombre del archivo donde se guardan los usuarios

def cargar_usuarios():
    # Si el archivo no existe, retorna una lista vacía
    if not os.path.exists(USUARIOS_FILE):
        return []
    # Si existe, lo abre y carga la lista de usuarios
    with open(USUARIOS_FILE, "r") as f:
        return json.load(f)

def guardar_usuarios(usuarios):
    # Guarda la lista de usuarios en el archivo en formato JSON
    with open(USUARIOS_FILE, "w") as f:
        json.dump(usuarios, f, indent=4)

@app.route('/registro', methods=['POST'])
def registro():
    datos = request.json  # Obtiene los datos enviados en formato JSON
    usuario = datos.get("usuario")         # Extrae el usuario
    contraseña = datos.get("contraseña")   # Extrae la contraseña
    email = datos.get("email")             # Extrae el email

    # Verifica que ningún campo esté vacío
    if not usuario or not contraseña or not email:
        return jsonify({"exito": False, "mensaje": "Faltan datos"}), 400

    usuarios = cargar_usuarios()  # Carga la lista de usuarios
    # Verifica si el usuario ya existe
    if any(u["usuario"] == usuario for u in usuarios):
        return jsonify({"exito": False, "mensaje": "Usuario ya existe"}), 409

    # Agrega el nuevo usuario a la lista
    usuarios.append({"usuario": usuario, "contraseña": contraseña, "email": email})
    guardar_usuarios(usuarios)  # Guarda la lista actualizada

    return jsonify({"exito": True, "mensaje": "Registro exitoso"})  # Responde con éxito

@app.route('/inicio_sesion', methods=['POST'])
def iniciar_sesion():
    datos = request.json  # Obtiene los datos enviados en formato JSON
    usuario = datos.get("usuario")         # Extrae el usuario
    contraseña = datos.get("contraseña")   # Extrae la contraseña

    usuarios = cargar_usuarios()  # Carga la lista de usuarios
    # Busca un usuario que coincida con usuario y contraseña
    for u in usuarios:
        if u["usuario"] == usuario and u["contraseña"] == contraseña:
            return jsonify({"exito": True, "mensaje": "Inicio de sesión exitoso"})
    # Si no encuentra coincidencia, responde con error
    return jsonify({"exito": False, "mensaje": "Usuario o contraseña incorrectos"}), 401

def obtener_ip():
    # Obtiene la IP local de la máquina para construir la URL del QR
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))  # Se conecta a un servidor externo para obtener la IP local
        return s.getsockname()[0]   # Retorna la IP local
    finally:
        s.close()                   # Cierra el socket

@app.route('/generar_qr')
def generar_qr():
    token = str(uuid.uuid4())   # Genera un token único
    TOKENS_VALIDOS.add(token)   # Lo agrega al conjunto de tokens válidos
    url = f"http://{obtener_ip()}:5000/?token={token}"  # Construye la URL con el token
    qrcode.make(url).save("qr_token.png")  # Genera y guarda el QR en un archivo
    return jsonify({"token": token, "url": url})  # Devuelve el token y la URL

@app.route('/')
def procesar_token():
    token = request.args.get('token')  # Obtiene el token de la URL
    if not token:
        return "Token no proporcionado."  # Si no hay token, responde con error
    if token in TOKENS_VALIDOS:
        TOKENS_VALIDOS.remove(token)     # Elimina el token de válidos
        TOKENS_USADOS.add(token)         # Lo agrega a usados
        return "Token válido. Autenticación confirmada. Puedes cerrar esta pestaña."
    else:
        return "Token inválido o ya usado."  # Si el token no es válido, responde con error

@app.route('/estado_token/<token>')
def estado_token(token):
    # Devuelve el estado del token: pendiente, concedido o denegado
    if token in TOKENS_VALIDOS:
        return jsonify({"acceso": "pendiente"})
    elif token in TOKENS_USADOS:
        return jsonify({"acceso": "concedido"})
    else:
        return jsonify({"acceso": "denegado"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Inicia el servidor Flask en todas las interfaces, puerto 5000
from flask import Flask, render_template, request, redirect, flash, jsonify, session, request, make_response
from flask_jwt import JWT, jwt_required, current_identity
import controlador_discos
import controlador_usuarios
import json, requests

#pip install Flask-JWT
#pip install Flask==2.3.3
#pip install PyJWT
#pip install pymysql



class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
    def __str__(self):
        return "User(id='%s')" % self.id

def authenticate(username, password):
    usuario = controlador_usuarios.obtener_usuario_por_email(username)
    user = None
    if usuario:
        user = User(usuario["id"], usuario["email"], usuario["password"])
    if user and user.password.encode('utf-8') == password.encode('utf-8'):
        return user

def identity(payload):
    user_id = payload['identity']
    usuario = controlador_usuarios.obtener_usuario_por_id(user_id)
    user = None
    if usuario:
        user = User(usuario["id"], usuario["email"], usuario["password"])
    return user


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'

jwt = JWT(app, authenticate, identity)


@app.route("/agregar_disco")
def formulario_agregar_disco():
    return render_template("agregar_disco.html")

@app.route("/guardar_disco", methods=["POST"])
def guardar_disco():
    codigo = request.form["codigo"]
    nombre = request.form["nombre"]
    artista = request.form["artista"]
    precio = request.form["precio"]
    genero = request.form["genero"]
    controlador_discos.insertar_disco(codigo, nombre, artista, precio, genero)
    # De cualquier modo, y si todo fue bien, redireccionar
    return redirect("/discos")


@app.route("/discos")
def discos():
    discos = controlador_discos.obtener_discos()
    return render_template("discos.html", discos=discos)


@app.route("/eliminar_disco", methods=["POST"])
def eliminar_disco():
    controlador_discos.eliminar_disco(request.form["id"])
    return redirect("/discos")


@app.route("/formulario_editar_disco/<int:id>")
def editar_disco(id):
    # Obtener el disco por ID
    disco = controlador_discos.obtener_disco_por_id(id)
    return render_template("editar_disco.html", disco=disco)


@app.route("/actualizar_disco", methods=["POST"])
def actualizar_disco():
    id = request.form["id"]
    codigo = request.form["codigo"]
    nombre = request.form["nombre"]
    artista = request.form["artista"]
    precio = request.form["precio"]
    genero = request.form["genero"]
    controlador_discos.actualizar_disco(codigo, nombre, artista, precio, genero, id)
    return redirect("/discos")

@app.route("/probarjsoninterno")
def probarjsoninterno():
    try:


        info = json.loads(datos)
        #print('Total de usuarios:', len(info))
        cadena = 'Total de usuarios: %s<br>' % str(len(info))
        for elemento in info:
            cadena += 'Nombre %s<br>' % elemento['nombre']
            cadena += 'Id %s<br>' % elemento['id']
            cadena += 'Atributo %s<br>' % elemento['x']
            #print('Nombre', elemento['nombre'])
            #print('Id', elemento['id'])
            #print('Atributo', elemento['x'])
        return cadena
    except Exception as e:
        return repr(e)


@app.route("/probarjsonexterno")
def probarjsonexterno():
    try:
        url = "https://jsonplaceholder.typicode.com/posts"
        response = requests.get(url)
        response.raise_for_status()
        json_data = response.json()
        cadena = 'Total: %s<br>' % str(len(json_data))
        return cadena
    except Exception as e:
        return repr(e)

@app.route("/promediodepalabrasxatributobodydelurl")
def promediodepalabrasxatributobodydelurl():
    try:
        url = "https://jsonplaceholder.typicode.com/posts"
        response = requests.get(url)
        response.raise_for_status()
        json_data = response.json()
        #cadena = 'Total: %s<br>' % str(len(json_data))
        cant = 0
        for elemento in json_data:
            cant += len(elemento['body'].split(' '))
        cadena = 'Palabras en promedio por atributo body: %s<br>' % str(cant/len(json_data))
        return cadena
    except Exception as e:
        return repr(e)

@app.route("/procesarjsonexterno2")
def procesarjsonexterno2():
    try:
        url = "https://jsonplaceholder.typicode.com/posts"
        response = requests.get(url)
        response.raise_for_status()
        json_data = response.json()
        # cadena = 'Total: %s<br>' % str(len(json_data))
        #cant = 0
        todo = ""
        for elemento in json_data:
            dominios = dict()
            #cant += len(elemento['body'].split(' '))
            url1 = "https://jsonplaceholder.typicode.com/comments?postId=%s" % elemento['id']
            response1 = requests.get(url1)
            response1.raise_for_status()
            json_data1 = response1.json()
            for comentario in json_data1:
                dom = comentario['email'].split('@')[1].split('.')[-1]
                dominios[dom] = dominios.get(dom, 0) + 1

            cadena = str(elemento['id'])
            for clave in dominios:
                cadena += "- .%s (%s)" % (clave, str(dominios[clave]))
            cadena += "<br>"
            todo += cadena
        return todo
    except Exception as e:
        return repr(e)

@app.route("/api_obtenerdisco", methods=['POST'])
@app.route("/api_obtenerdisco/<int:id>")
def pi_obtenerdisco(id=0):
    rpta = dict()
    try:
        if request.method == 'POST':
            id = request.json["id"]
        disco = controlador_discos.obtener_disco_por_id(id,True)
        if disco:
            mensaje = "Disco Obtenido correctamente"
        else:
            disco = {}
            mensaje = "No existe el disco consultado"
        rpta["code"] = 1
        rpta["data"] = disco
        rpta["message"] = "Disco obenido correctamente"
    except Exception as e:
        rpta["code"] = 0
        rpta["data"] = {}
        rpta["message"] = "Ocurrio el siguiente error: %s" % repr(e)
    return jsonify(rpta)


@app.route("/api_guardar_disco", methods=["POST"])
@jwt_required()
def api_guardar_disco():
    #rpta = dict()
    try:
        codigo = request.json["codigo"]
        nombre = request.json["nombre"]
        artista = request.json["artista"]
        precio = request.json["precio"]
        genero = request.json["genero"]
        idgenerado = controlador_discos.insertar_disco(codigo, nombre, artista, precio, genero)
        return jsonify({"code": 1,
                        "data": {"idgenerado": idgenerado},
                        "message": "Disco guardado correctamente" })
    except Exception as e:
        return jsonify({"code": 1,
                        "data": {},
                        "message": "Ocurrio el siguiente error: %s" % repr(e) })




@app.route("/api_actualizar_disco", methods=["POST"])
def api_actualizar_disco():
    try:
        id = request.json["id"]
        codigo = request.json["codigo"]
        nombre = request.json["nombre"]
        artista = request.json["artista"]
        precio = request.json["precio"]
        genero = request.json["genero"]

        controlador_discos.actualizar_disco(codigo, nombre, artista, precio, genero, id)

        return jsonify({
            "code": 1,
            "data": {},
            "message": "Disco actualizado correctamente"
        })
    except Exception as e:
        return jsonify({
            "code": 1,
            "data": {},
            "message": "Ocurrió el siguiente error: %s" % repr(e)
        })


@app.route("/")
@app.route("/login")
def login():
    if 'username' in session:
        return redirect("/discos")
    else:
        return render_template("login.html")


@app.route("/procesar_login", methods=["POST"])
def procesar_login():
    username = request.form["usuario"]
    password = request.form["contrasena"]
    usuario = controlador_usuarios.obtener_usuario_por_email(username)

    if usuario and usuario["password"] == password:
        discos = controlador_discos.obtener_discos()
        resp = make_response(render_template("discos.html", discos=discos))
        resp.set_cookie('username', username)
        return resp
    else:
        return redirect("/login")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/procesar_signup", methods=["POST"])
def procesar_signup():
    username = request.form["usuario"]
    password = request.form["contrasena"]
    confpassword = request.form["confcontrasena"]
    usuario = controlador_usuarios.obtener_usuario_por_email(username, password)
    if usuario or (password != confpassword):
        return redirect("/login")
    else:
        controlador_usuarios.obtener_usuario_por_email(username, password)
        return redirect("/discos")
    return redirect("/login")

@app.route("/procesar_logout", methods=["POST"])
def procesar_logout():
    session.pop('username',None)
    resp = make_response(render_template("login.html"))
    resp.set_cookie('username', '', expires=0)
    return resp



# Iniciar el servidor
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)


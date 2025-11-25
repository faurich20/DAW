from bd import obtener_conexion


#################################################################################################
def obtener_usuario_por_id(id):
    conexion = obtener_conexion(True)
    usuario = None
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT id, email, password FROM users WHERE id = %s", (id,))
        usuario = cursor.fetchone()
    conexion.close()
    return usuario

def obtener_usuario_por_email(email):
    conexion = obtener_conexion(True)
    usuario = None
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT id, email, password FROM users WHERE email = %s", (email,))
        usuario = cursor.fetchone()
    conexion.close()
    return usuario


#################################################################################################
def actualizar_usuario(email, password, id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE users SET email = %s, password = %s WHERE id = %s",
                       (email, password, id))
    conexion.commit()
    conexion.close()


def insertar_usuario(username, password):
    id=0
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("INSERT INTO users(email, password) VALUES (%s, %s)",
                       (username, password))
    id = conexion.insert_id()
    conexion.commit()
    conexion.close()
    return id

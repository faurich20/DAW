from bd import obtener_conexion
import requests

# URLs de las APIs
URL_todos = "https://jsonplaceholder.typicode.com/todos"
URL_usuarios = "https://jsonplaceholder.typicode.com/users"
URL_posts = "https://jsonplaceholder.typicode.com/posts"
URL_comentarios = "https://jsonplaceholder.typicode.com/comments"


def procesar_pendientes(porcentaje_minimo):
    """
    Procesa usuarios con porcentaje mínimo de tareas completadas
    y guarda sus comentadores en BD (Lógica anterior)
    """
    # Descargar todos
    response_todos = requests.get(URL_todos)
    response_todos.raise_for_status()
    todos = response_todos.json()
    
    # Descargar usuarios
    response_usuarios = requests.get(URL_usuarios)
    response_usuarios.raise_for_status()
    usuarios = response_usuarios.json()
    
    # Descargar posts
    response_posts = requests.get(URL_posts)
    response_posts.raise_for_status()
    posts = response_posts.json()
    
    # Descargar comentarios
    response_comentarios = requests.get(URL_comentarios)
    response_comentarios.raise_for_status()
    comentarios = response_comentarios.json()
    
    # Calcular porcentaje de tareas completadas por usuario
    usuarios_tareas = {}
    for todo in todos:
        userId = todo['userId']
        if userId not in usuarios_tareas:
            usuarios_tareas[userId] = {'total': 0, 'completadas': 0}
        usuarios_tareas[userId]['total'] += 1
        if todo['completed']:
            usuarios_tareas[userId]['completadas'] += 1
    
    # Filtrar usuarios que cumplen el porcentaje minimo
    usuarios_filtrados = []
    for userId, tareas in usuarios_tareas.items():
        porcentaje = tareas['completadas'] / tareas['total']
        if porcentaje >= porcentaje_minimo:
            # Buscar username
            username = None
            for u in usuarios:
                if u['id'] == userId:
                    username = u['username']
                    break
            usuarios_filtrados.append({
                'userId': userId,
                'username': username,
                'porcentaje': porcentaje
            })
    
    # Guardar en BD
    conexion = obtener_conexion()
    id_proceso = 0
    
    with conexion.cursor() as cursor:
        # Obtener el siguiente id_proceso (MAX + 1) ANTES de cualquier operación
        cursor.execute('SELECT COALESCE(MAX(id_proceso), 0) + 1 FROM usuarios_procesos')
        result = cursor.fetchone()
        id_proceso = result[0] if result else 1
        
        # Para cada usuario filtrado, buscar comentarios en sus posts
        for usuario in usuarios_filtrados:
            userId = usuario['userId']
            username = usuario['username']
            porcentaje = usuario['porcentaje']
            
            # Insertar usuario en BD con el id_proceso
            cursor.execute('INSERT INTO usuarios_procesos (id_proceso, userId, username, porcentaje) VALUES (%s, %s, %s, %s)',
                         (id_proceso, userId, username, porcentaje))
            # OBTENER ID INMEDIATAMENTE DESPUÉS DEL INSERT, ANTES DEL COMMIT
            id_usuario_proceso = conexion.insert_id()
            
            # Buscar posts del usuario
            posts_usuario = []
            for post in posts:
                if post['userId'] == userId:
                    posts_usuario.append(post['id'])
            
            # Buscar comentarios en esos posts
            emails_comentadores = []
            for comentario in comentarios:
                if comentario['postId'] in posts_usuario:
                    email = comentario['email']
                    if email not in emails_comentadores:
                        emails_comentadores.append(email)
                        cursor.execute('INSERT INTO comentadores (id_usuario_proceso, email) VALUES (%s, %s)',
                                     (id_usuario_proceso, email))
    
    # Hacer commit final de todas las operaciones
    conexion.commit()
    conexion.close()
    
    return id_proceso


#FUNCIONES PARA EXAMEN 3 - EJERCICIO 02
def obtener_detalle_proceso(id_proceso):
    """
    Obtiene el detalle de un proceso por su id
    """
    conexion = obtener_conexion()
    data = []
    with conexion.cursor() as cursor:
        # Buscar usuarios del proceso (filtrar por id_proceso exacto)
        cursor.execute('SELECT id, userId, username, porcentaje FROM usuarios_procesos WHERE id_proceso = %s', (id_proceso,))
        usuarios = cursor.fetchall()
        
        for usuario in usuarios:
            id_usuario_proceso = usuario[0]
            userId = usuario[1]
            username = usuario[2]
            porcentaje = float(usuario[3])
            
            # Buscar comentadores
            cursor.execute('SELECT email FROM comentadores WHERE id_usuario_proceso = %s', (id_usuario_proceso,))
            comentadores_rows = cursor.fetchall()
            comentadores = []
            for row in comentadores_rows:
                comentadores.append(row[0])
            
            data.append({
                'userId': userId,
                'username': username,
                'porcentaje': porcentaje,
                'comentadores': comentadores
            })
    
    conexion.close()
    
    return data


def procesar_evaluar_fepa(porcentaje_minimo):
    """
    Procesa usuarios con porcentaje mínimo de tareas completadas,
    calcula promedio de palabras por línea en comentarios y guarda en BD (Tablas FEPA)
    """
    # Descargar todos
    response_todos = requests.get(URL_todos)
    response_todos.raise_for_status()
    todos = response_todos.json()
    
    # Descargar posts
    response_posts = requests.get(URL_posts)
    response_posts.raise_for_status()
    posts = response_posts.json()
    
    # Descargar comentarios
    response_comentarios = requests.get(URL_comentarios)
    response_comentarios.raise_for_status()
    comentarios = response_comentarios.json()
    
    # Calcular porcentaje de tareas completadas por usuario
    usuarios_tareas = {}
    for todo in todos:
        userId = todo['userId']
        if userId not in usuarios_tareas:
            usuarios_tareas[userId] = {'total': 0, 'completadas': 0}
        usuarios_tareas[userId]['total'] += 1
        if todo['completed']:
            usuarios_tareas[userId]['completadas'] += 1
    
    # Filtrar usuarios que cumplen el porcentaje minimo
    usuarios_filtrados = []
    for userId, tareas in usuarios_tareas.items():
        porcentaje = tareas['completadas'] / tareas['total']
        if porcentaje >= porcentaje_minimo:
            usuarios_filtrados.append({
                'userId': userId,
                'porcentaje': porcentaje
            })
    
    # Guardar en BD
    conexion = obtener_conexion()
    ideval = 0
    
    with conexion.cursor() as cursor:
        # Insertar evaluacion con fecha y porcentaje
        cursor.execute('INSERT INTO evaluacion_fepa (fechahora, porcentaje) VALUES (NOW(), %s)', (porcentaje_minimo,))
        ideval = conexion.insert_id()
        
        # Para cada usuario filtrado
        for usuario in usuarios_filtrados:
            userId = usuario['userId']
            
            # Buscar posts del usuario
            posts_usuario = []
            for post in posts:
                if post['userId'] == userId:
                    posts_usuario.append(post)
            
            # Para cada post del usuario
            for post in posts_usuario:
                postId = post['id']
                
                # Buscar comentarios del post
                comentarios_post = []
                for comentario in comentarios:
                    if comentario['postId'] == postId:
                        comentarios_post.append(comentario)
                
                # Calcular promedio de palabras por línea para cada comentario
                comentarios_con_promedio = []
                for comentario in comentarios_post:
                    body = comentario['body']
                    lineas = body.split('\n')
                    
                    total_palabras = 0
                    for linea in lineas:
                        palabras = linea.split()
                        total_palabras += len(palabras)
                    
                    promedio = total_palabras / len(lineas) if len(lineas) > 0 else 0
                    
                    comentarios_con_promedio.append({
                        'email': comentario['email'],
                        'promedio': promedio
                    })
                
                # Ordenar por promedio de mayor a menor
                comentarios_con_promedio.sort(key=lambda x: x['promedio'], reverse=True)
                
                # Seleccionar los dos comentarios con mayor promedio
                top_2 = comentarios_con_promedio[:2]
                
                # Guardar en BD
                for com in top_2:
                    cursor.execute('INSERT INTO evaldet_fepa (ideval, userId, email, promedio) VALUES (%s, %s, %s, %s)',
                                 (ideval, userId, com['email'], com['promedio']))
    
    conexion.commit()
    conexion.close()
    
    return ideval


def obtener_detalle_evaluacion(ideval):
    """
    Obtiene el detalle completo de una evaluación por su ideval
    Estructura:
    {
        "fechahora": "YYYY-MM-DD HH:MM",
        "ideval": 1,
        "detalle": [...],
        "porcentaje": 0.8
    }
    """
    conexion = obtener_conexion()
    resultado = {}
    
    with conexion.cursor() as cursor:
        # 1. Obtener datos de la cabecera (evaluacion_fepa)
        cursor.execute('SELECT fechahora, porcentaje FROM evaluacion_fepa WHERE ideval = %s', (ideval,))
        cabecera = cursor.fetchone()
        
        if not cabecera:
            conexion.close()
            return None
            
        # Formatear fecha a string (YYYY-MM-DD HH:MM)
        fechahora = cabecera[0]
        if fechahora:
            if hasattr(fechahora, 'strftime'):
                fechahora = fechahora.strftime('%Y-%m-%d %H:%M')
            else:
                fechahora = str(fechahora)
        else:
            fechahora = None
            
        porcentaje = float(cabecera[1])
        
        resultado['fechahora'] = fechahora
        resultado['ideval'] = ideval
        resultado['detalle'] = [] 
        resultado['porcentaje'] = porcentaje
        
        # 2. Obtener detalles (evaldet_fepa)
        cursor.execute('SELECT id, ideval, userId, email, promedio FROM evaldet_fepa WHERE ideval = %s', (ideval,))
        detalles_rows = cursor.fetchall()
        
        detalles = []
        for row in detalles_rows:
            detalles.append({
                'id': row[0],
                'ideval': row[1],
                'userId': row[2],
                'email': row[3],
                'promedio': float(row[4])
            })
            
        resultado['detalle'] = detalles
    
    conexion.close()
    
    return resultado
import requests

#construir una api que devuelva dos claces y dos valores
#{
#    "primero": "Juan Perez",
#    "ultimo": "Marco Martinez"
#}
# Donde "primero", es el usuario creador de la publicacion con el comentario con más
#palabras. Donde "ultimo", esel usuario creador de la publicacion con el comentario con menos
#palabras.

#tengo entendido que:

#api para https://jsonplaceholder.typicode.com/comments tiene como datos
#{
    #"postId": in de la publicacion
    #"id": 
    #"name": 
    #"email": 
    #"body": aqui esta el comentario de cada publicacion
#}

#https://jsonplaceholder.typicode.com/posts son las publicaciones y tiene los atributos:
#{
    #"userId": 1,  id del usuario creador de la publicacion
    #"id": 1,
    #"title": 
    #"body": 
#}

#http://jsonplaceholder.typicode.com/users son los usuario tiene los datos: 
#{
    #"id":  su id del creado
    #"name":  aqui obtenemos el nombre
    #"username": 
    #"email": 
    #"address": {
            #    "street":
            #    "suite": 
            #    "city": 
            #    "zipcode": 
            #    "geo": {
            #        "lat": 
            #        "lng": 
    #           }
    #},
    #"phone": 
    #"website": 
    #"company": {
            #    "name": 
            #    "catchPhrase": 
            #    "bs": 
                #}
#}


# URLs
URL_COMMENTS = "https://jsonplaceholder.typicode.com/comments"
URL_POSTS = "https://jsonplaceholder.typicode.com/posts"
URL_USERS = "https://jsonplaceholder.typicode.com/users"

try:
    # Descargar comentarios
    response_comments = requests.get(URL_COMMENTS)
    response_comments.raise_for_status()
    comments = response_comments.json()

    # Descargar posts
    response_posts = requests.get(URL_POSTS)
    response_posts.raise_for_status()
    posts = response_posts.json()

    # Descargar usuarios
    response_users = requests.get(URL_USERS)
    response_users.raise_for_status()
    users = response_users.json()

    # -------------------------------
    # 1. Buscar comentario con más y menos palabras
    # -------------------------------

    mayor_palabras = -1
    menor_palabras = 999999999

    comentario_max = None
    comentario_min = None

    for comentario in comments:
        texto = comentario["body"]

        # split() separa por espacios, saltos de línea "\n", "\t", etc.
        cantidad = len(texto.split())

        if cantidad > mayor_palabras:
            mayor_palabras = cantidad
            comentario_max = comentario

        if cantidad < menor_palabras:
            menor_palabras = cantidad
            comentario_min = comentario

    # -------------------------------
    # 2. Conseguir usuario creador del post correspondiente
    # -------------------------------

    def obtener_usuario(postId):
        # Encontrar el post
        post_encontrado = None
        for p in posts:
            if p["id"] == postId:
                post_encontrado = p
                break

        if post_encontrado is None:
            return None

        id_usuario = post_encontrado["userId"]

        # Buscar el usuario
        for u in users:
            if u["id"] == id_usuario:
                return u["name"]

        return None

    usuario_max = obtener_usuario(comentario_max["postId"])
    usuario_min = obtener_usuario(comentario_min["postId"])

    # -------------------------------
    # 3. Construir respuesta final
    # -------------------------------

    resultado = {
        "primero": usuario_max,
        "ultimo": usuario_min
    }

    print(resultado)

except requests.exceptions.RequestException as e:
    print(f"Error fetching data: {e}")

except ValueError as e:
    print(f"Error parsing JSON: {e}")


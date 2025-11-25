import pymysql

HOST = 'faurich20.mysql.pythonanywhere-services.com'
USER = 'root'#'faurich20'
PASSWORD = ''#'abcDEF$123'
DB = 'faurich20$dawb_datos'
PORT = 3327

def obtener_conexion(con_dict=False):
    if con_dict:
        clasecursor = pymysql.cursors.DictCursor
    else:
        clasecursor = pymysql.cursors.Cursor
    return pymysql.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        db=DB,
        port=PORT,
        cursorclass=clasecursor
    )
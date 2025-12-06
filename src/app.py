from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_cors import CORS

from config import config

app = Flask(__name__)
CORS(app, resources={r"/propiedades/*": {"origins": "http://localhost:4200"}})

conexion = MySQL(app)

def leer_propiedad_bd(id_propiedad):
    try:
        cursor = conexion.connection.cursor()
        sql = f"SELECT id_propiedad, titulo, descripcion, precio, direccion, ciudad, tipo, imagen, estado FROM propiedades WHERE id_propiedad = {id_propiedad}"
        cursor.execute(sql)
        datos = cursor.fetchone()

        if datos is not None:
            propiedad = {
                'id_propiedad': datos[0],
                'titulo': datos[1],
                'descripcion': datos[2],
                'precio': datos[3],
                'direccion': datos[4],
                'ciudad': datos[5],
                'tipo': datos[6],
                'imagen': datos[7],
                'estado': datos[8]
            }
            return propiedad
        else:
            return None

    except Exception as ex:
        return None


@app.route('/propiedades', methods=['GET'])
def listar_propiedades():
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT id_propiedad, titulo, descripcion, precio, direccion, ciudad, tipo, imagen, estado FROM propiedades"
        cursor.execute(sql)
        datos = cursor.fetchall()

        propiedades = []
        for fila in datos:
            propiedad = {
                'id_propiedad': fila[0],
                'titulo': fila[1],
                'descripcion': fila[2],
                'precio': fila[3],
                'direccion': fila[4],
                'ciudad': fila[5],
                'tipo': fila[6],
                'imagen': fila[7],
                'estado': fila[8]
            }
            propiedades.append(propiedad)

        return jsonify({'propiedades': propiedades, 'mensaje': 'Propiedades listadas', 'exito': True})

    except Exception as ex:
        return jsonify({'mensaje': 'Error', "exito": False})


@app.route('/propiedades/<id_prop>', methods=['GET'])
def leer_propiedad(id_prop):
    try:
        propiedad = leer_propiedad_bd(id_prop)
        if propiedad is not None:
            return jsonify({'propiedad': propiedad, 'mensaje': 'Propiedad encontrada', 'exito': True})
        else:
            return jsonify({'mensaje': 'Propiedad no encontrada', 'exito': False})

    except Exception as ex:
        return jsonify({'mensaje': 'Error', 'exito': False})


@app.route('/propiedades', methods=['POST'])
def registrar_propiedad():
    try:
        cursor = conexion.connection.cursor()

        sql = """INSERT INTO propiedades (titulo, descripcion, precio, direccion, ciudad, tipo, imagen, estado)
                 VALUES ('{0}', '{1}', {2}, '{3}', '{4}', '{5}', '{6}', '{7}')""".format(
            request.json['titulo'],
            request.json['descripcion'],
            request.json['precio'],
            request.json['direccion'],
            request.json['ciudad'],
            request.json['tipo'],
            request.json.get('imagen', ''),
            request.json.get('estado', 'disponible')
        )

        cursor.execute(sql)
        conexion.connection.commit()

        return jsonify({'mensaje': 'Propiedad registrada', 'exito': True})

    except Exception as ex:
        return jsonify({'mensaje': 'Error', "exito": False})


@app.route('/propiedades/<id_prop>', methods=['PUT'])
def actualizar_propiedad(id_prop):
    try:
        propiedad = leer_propiedad_bd(id_prop)
        if propiedad is not None:

            cursor = conexion.connection.cursor()
            sql = """UPDATE propiedades SET titulo='{0}', descripcion='{1}', precio={2},
                     direccion='{3}', ciudad='{4}', tipo='{5}', imagen='{6}', estado='{7}'
                     WHERE id_propiedad={8}""".format(
                request.json['titulo'],
                request.json['descripcion'],
                request.json['precio'],
                request.json['direccion'],
                request.json['ciudad'],
                request.json['tipo'],
                request.json.get('imagen', propiedad['imagen']),
                request.json.get('estado', propiedad['estado']),
                id_prop
            )

            cursor.execute(sql)
            conexion.connection.commit()

            return jsonify({'mensaje': 'Propiedad actualizada', 'exito': True})

        else:
            return jsonify({'mensaje': 'Propiedad no encontrada', 'exito': False})

    except Exception as ex:
        return jsonify({'mensaje': "Error", 'exito': False})


@app.route('/propiedades/<id_prop>', methods=['DELETE'])
def eliminar_propiedad(id_prop):
    try:
        propiedad = leer_propiedad_bd(id_prop)
        if propiedad is not None:

            cursor = conexion.connection.cursor()
            sql = f"DELETE FROM propiedades WHERE id_propiedad = {id_prop}"
            cursor.execute(sql)
            conexion.connection.commit()

            return jsonify({'mensaje': "Propiedad eliminada", 'exito': True})

        else:
            return jsonify({'mensaje': "Propiedad no encontrada", 'exito': False})

    except Exception as ex:
        return jsonify({'mensaje': "Error", 'exito': False})

##############################################
# Agrega esto en tu app.py después de los endpoints de propiedades

@app.route('/favoritos/<int:usuario_id>', methods=['GET'])
def obtener_favoritos(usuario_id):
    try:
        cursor = conexion.connection.cursor()
        sql = """SELECT p.id_propiedad, p.titulo, p.descripcion, p.precio, 
                        p.direccion, p.ciudad, p.tipo, p.imagen, p.estado
                 FROM favoritos f
                 JOIN propiedades p ON f.id_propiedad = p.id_propiedad
                 WHERE f.id_usuario = {0}""".format(usuario_id)
        
        cursor.execute(sql)
        favoritos = cursor.fetchall()
        
        resultado = []
        for fav in favoritos:
            propiedad = {
                'id_propiedad': fav[0],
                'titulo': fav[1],
                'descripcion': fav[2],
                'precio': float(fav[3]),
                'direccion': fav[4],
                'ciudad': fav[5],
                'tipo': fav[6],
                'imagen': fav[7],
                'estado': fav[8]
            }
            resultado.append(propiedad)
        
        return jsonify({'favoritos': resultado, 'mensaje': 'Favoritos listados', "exito": True})
        
    except Exception as ex:
        return jsonify({'mensaje': 'error', "exito": False})

@app.route('/favoritos/agregar', methods=['POST'])
def agregar_favorito():
    try:
        datos = request.json
        cursor = conexion.connection.cursor()
        
        # Verificar si ya es favorito
        sql_check = """SELECT id_favorito FROM favoritos 
                       WHERE id_usuario = {0} AND id_propiedad = {1}""".format(
                       datos['id_usuario'], datos['id_propiedad'])
        cursor.execute(sql_check)
        
        if cursor.fetchone():
            return jsonify({'mensaje': 'Ya está en favoritos', "exito": False})
        
        # Agregar a favoritos
        sql_insert = """INSERT INTO favoritos (id_usuario, id_propiedad)
                        VALUES ({0}, {1})""".format(
                        datos['id_usuario'], datos['id_propiedad'])
        
        cursor.execute(sql_insert)
        conexion.connection.commit()
        
        return jsonify({'mensaje': 'Agregado a favoritos', "exito": True})
        
    except Exception as ex:
        return jsonify({'mensaje': 'error', "exito": False})

@app.route('/favoritos/eliminar/<int:favorito_id>', methods=['DELETE'])
def eliminar_favorito(favorito_id):
    try:
        cursor = conexion.connection.cursor()
        sql = "DELETE FROM favoritos WHERE id_favorito = {0}".format(favorito_id)
        
        cursor.execute(sql)
        conexion.connection.commit()
        
        return jsonify({'mensaje': 'Eliminado de favoritos', "exito": True})
        
    except Exception as ex:
        return jsonify({'mensaje': 'error', "exito": False})

####################################################
@app.route('/citas/agendar', methods=['POST'])
def agendar_cita():
    try:
        datos = request.json
        cursor = conexion.connection.cursor()
        
        sql = """INSERT INTO citas (id_usuario, id_propiedad, fecha, hora, estado, notas)
                 VALUES (%s, %s, %s, %s, 'pendiente', %s)"""
        
        valores = (
            datos.get('id_usuario', 1),  # Temporal, después del login
            datos['propiedad_id'],
            datos['fecha'],
            datos['hora'],
            datos.get('notas', '')
        )
        
        cursor.execute(sql, valores)
        conexion.connection.commit()
        
        return jsonify({'mensaje': 'Cita agendada', 'id': cursor.lastrowid, 'exito': True})
        
    except Exception as ex:
        return jsonify({'mensaje': 'error', 'exito': False})


################################################
@app.route('/dashboard/admin', methods=['GET'])
def dashboard_admin():
    try:
        cursor = conexion.connection.cursor()
        stats = {}
        
        # Propiedades activas
        cursor.execute("SELECT COUNT(*) FROM propiedades WHERE estado = 'disponible'")
        stats['propiedades_activas'] = cursor.fetchone()[0]
        
        # Tours VR (simulado - contar propiedades con tipo específico)
        cursor.execute("SELECT COUNT(*) FROM propiedades WHERE tipo = 'casa' OR tipo = 'departamento'")
        stats['tours_vr'] = cursor.fetchone()[0]
        
        # Clientes
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol = 'cliente'")
        stats['clientes'] = cursor.fetchone()[0]
        
        # Citas hoy
        cursor.execute("SELECT COUNT(*) FROM citas WHERE fecha = CURDATE()")
        stats['citas_hoy'] = cursor.fetchone()[0]
        
        return jsonify({'estadisticas': stats, 'exito': True})
        
    except Exception as ex:
        return jsonify({'mensaje': 'error', 'exito': False})

#########################################################
@app.route('/dashboard/usuario/<int:usuario_id>', methods=['GET'])
def dashboard_usuario(usuario_id):
    try:
        cursor = conexion.connection.cursor()
        stats = {}
        
        # Citas agendadas del usuario
        cursor.execute("SELECT COUNT(*) FROM citas WHERE id_usuario = %s", (usuario_id,))
        stats['citas_agendadas'] = cursor.fetchone()[0]
        
        # Recorridos hechos (citas completadas)
        cursor.execute("SELECT COUNT(*) FROM citas WHERE id_usuario = %s AND estado = 'completada'", (usuario_id,))
        stats['recorridos_hechos'] = cursor.fetchone()[0]
        
        # Favoritos
        cursor.execute("SELECT COUNT(*) FROM favoritos WHERE id_usuario = %s", (usuario_id,))
        stats['favoritos'] = cursor.fetchone()[0]
        
        # Tours VR usados (simulado)
        stats['usos_tecnologia'] = stats['recorridos_hechos'] * 2  # Ejemplo
        
        return jsonify({'estadisticas': stats, 'exito': True})
        
    except Exception as ex:
        return jsonify({'mensaje': 'error', 'exito': False})








def pagina_no_encontrada(error):
    return "<h1>La página que buscas no existe</h1>", 404


if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(404, pagina_no_encontrada)
    app.run()

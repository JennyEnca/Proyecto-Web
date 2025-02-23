from controllers.funciones_login import *
from app import app
from flask import render_template, request, flash, redirect, url_for, session,  jsonify
from mysql.connector.errors import Error


# Importando cenexión a BD
from controllers.funciones_home import *

@app.route('/lista-de-areas', methods=['GET'])
def lista_areas():
    if 'conectado' in session:
        return render_template('public/usuarios/lista_areas.html', areas=lista_areasBD(), dataLogin=dataLoginSesion())
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route("/lista-de-usuarios", methods=['GET'])
def usuarios():
    if 'conectado' in session:
        return render_template('public/usuarios/lista_usuarios.html',  resp_usuariosBD=lista_usuariosBD(), dataLogin=dataLoginSesion(), areas=lista_areasBD(), roles = lista_rolesBD())
    else:
        return redirect(url_for('inicioCpanel'))
    

#Ruta especificada para eliminar un usuario
@app.route('/borrar-usuario/<string:id>', methods=['GET'])
def borrarUsuario(id):
    resp = eliminarUsuario(id)
    if resp:
        flash('El Usuario fue eliminado correctamente', 'success')
        return redirect(url_for('usuarios'))
    
    
@app.route('/borrar-area/<string:id_area>/', methods=['GET'])
def borrarArea(id_area):
    resp = eliminarArea(id_area)
    if resp:
        flash('El Empleado fue eliminado correctamente', 'success')
        return redirect(url_for('lista_areas'))
    else:
        flash('Hay usuarios que pertenecen a esta área', 'error')
        return redirect(url_for('lista_areas'))


@app.route("/descargar-informe-accesos/", methods=['GET'])
def reporteBD():
    if 'conectado' in session:
        return generarReporteExcel()
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
@app.route("/reporte-accesos", methods=['GET'])
def reporteAccesos():
    if 'conectado' in session:
        userData = dataLoginSesion()
        return render_template('public/perfil/reportes.html',  reportes=dataReportes(),lastAccess=lastAccessBD(userData.get('cedula')), dataLogin=dataLoginSesion())

@app.route("/interfaz-clave", methods=['GET','POST'])
def claves():
    return render_template('public/usuarios/generar_clave.html', dataLogin=dataLoginSesion())
    
@app.route('/generar-y-guardar-clave/<string:id>', methods=['GET','POST'])
def generar_clave(id):
    print(id)
    clave_generada = crearClave()  # Llama a la función para generar la clave
    guardarClaveAuditoria(clave_generada,id)
    return clave_generada
#CREAR AREA
@app.route('/crear-area', methods=['GET','POST'])
def crearArea():
    if request.method == 'POST':
        area_name = request.form['nombre_area']  # Asumiendo que 'nombre_area' es el nombre del campo en el formulario
        resultado_insert = guardarArea(area_name)
        if resultado_insert:
            # Éxito al guardar el área
            flash('El Area fue creada correctamente', 'success')
            return redirect(url_for('lista_areas'))
            
        else:
            # Manejar error al guardar el área
            return "Hubo un error al guardar el área."
    return render_template('public/usuarios/lista_areas')

##ACTUALIZAR AREA
@app.route('/actualizar-area', methods=['POST'])
def updateArea():
    if request.method == 'POST':
        nombre_area = request.form['nombre_area']  # Asumiendo que 'nuevo_nombre' es el nombre del campo en el formulario
        id_area = request.form['id_area']
        resultado_update = actualizarArea(id_area, nombre_area)
        if resultado_update:
           # Éxito al actualizar el área
            flash('El actualizar fue creada correctamente', 'success')
            return redirect(url_for('lista_areas'))
        else:
            # Manejar error al actualizar el área
            return "Hubo un error al actualizar el área."

    return redirect(url_for('lista_areas'))
 
@app.route("/lista-estudiantes", methods=['GET'])
def lista_estudiantes():
    if 'conectado' in session:
        estudiantes = lista_estudiantesBD()  # Función para obtener los estudiantes desde la base de datos
        dataLogin = session.get('dataLogin')  # O cualquier otro método que uses para obtener los datos del usuario
        return render_template('public/usuarios/lista_estudiantes.html', resp_estudiantesBD=estudiantes, dataLogin=dataLogin)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


# Ruta para procesar el registro de un estudiante
@app.route("/registrar-estudiante", methods=['GET', 'POST'])
def registrar_estudiante():
    if 'conectado' in session:
        if request.method == 'POST':
            cedula = request.form['cedula']
            nombre = request.form['nombre']
            carrera = request.form['carrera']
            
            # Llamamos a la función para guardar al estudiante en la base de datos
            resp = guardarEstudiante(cedula, nombre, carrera)
            
            if resp:
                flash('Estudiante registrado con éxito', 'success')
                return redirect(url_for('lista_estudiantes'))
            else:
                flash('Hubo un error al registrar el estudiante.', 'error')
                return redirect(url_for('registrar_estudiante'))
        return render_template('public/usuarios/registro.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

# Ruta para eliminar un estudiante
@app.route("/borrar-estudiante/<int:id>", methods=['GET'])
def borrar_estudiante(id):
    if 'conectado' in session:
        resp = eliminarEstudiante(id)  # Función para eliminar el estudiante de la base de datos
        if resp:
            flash('Estudiante eliminado correctamente', 'success')
            return redirect(url_for('lista_estudiantes'))
        else:
            flash('Error al eliminar el estudiante.', 'error')
            return redirect(url_for('lista_estudiantes'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

# Ruta para mostrar el formulario de actualización
@app.route("/actualizar-estudiante/<int:id>", methods=['GET'])
def actualizar_estudiante(id):
    if 'conectado' in session:
        estudiante = obtener_estudiante_por_id(id)  # Obtén el estudiante por ID
        if estudiante:
            return render_template('public/usuarios/actualizar_estudiante.html', estudiante=estudiante)
        else:
            flash('Estudiante no encontrado.', 'error')
            return redirect(url_for('lista_estudiantes'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

# Ruta para procesar la actualización del estudiante
@app.route("/actualizar-estudiante/<int:id>", methods=['POST'])
def procesar_actualizacion_estudiante(id):
    if 'conectado' in session:
        cedula = request.form['cedula']
        nombre = request.form['nombre']
        carrera = request.form['carrera']
        
        # Llama a la función para actualizar al estudiante
        resp = actualizar_estudiante_db(id, cedula, nombre, carrera)
        
        if resp:
            flash('Estudiante actualizado con éxito', 'success')
            return redirect(url_for('lista_estudiantes'))
        else:
            flash('Hubo un error al actualizar el estudiante.', 'error')
            return redirect(url_for('actualizar_estudiante', id=id))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


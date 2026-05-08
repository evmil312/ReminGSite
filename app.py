from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

app = Flask(__name__)
app.secret_key = 'remin_g_secret_key'
app.config['GOOGLE_MAPS_API_KEY'] = os.getenv('GOOGLE_MAPS_API_KEY')


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'usuario'
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS avisos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            fecha TEXT NOT NULL,
            descripcion TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS costos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            concepto TEXT NOT NULL,
            precio TEXT NOT NULL
        )
    ''')
    conn.commit()

    cursor.execute("SELECT id FROM users WHERE email = 'admin@remingsite.com'")
    if not cursor.fetchone():
        cursor.execute(
            'INSERT INTO users (nombre, email, password, role) VALUES (?, ?, ?, ?)',
            ('Administrador', 'admin@remingsite.com', generate_password_hash('admin123'), 'admin')
        )

    cursor.execute("SELECT id FROM costos")
    if not cursor.fetchone():
        cursor.executemany(
            'INSERT INTO costos (concepto, precio) VALUES (?, ?)',
            [
                ('Inscripción anual', 'S/ 450'),
                ('Matricula por grado', 'S/ 180'),
                ('Uniforme oficial', 'S/ 250'),
                ('Material académico', 'S/ 120')
            ]
        )

    cursor.execute("SELECT id FROM eventos")
    if not cursor.fetchone():
        cursor.executemany(
            'INSERT INTO eventos (titulo, fecha, descripcion) VALUES (?, ?, ?)',
            [
                ('Inicio de clases', '05/03/2026', 'Apertura del año escolar con bienvenida a estudiantes y familias.'),
                ('Día de la Familia', '20/06/2026', 'Evento especial donde se presenta el trabajo estudiantil.'),
                ('Entrega de boletas', '15/12/2026', 'Cierre de semestre y entrega de evaluaciones finales.')
            ]
        )

    cursor.execute("SELECT id FROM avisos")
    if not cursor.fetchone():
        cursor.executemany(
            'INSERT INTO avisos (titulo, descripcion, fecha) VALUES (?, ?, ?)',
            [
                ('Nueva plataforma de comunicación', 'Hemos lanzado un portal seguro para estudiantes y padres.', '01/04/2026'),
                ('Reunión de padres', 'Convocatoria para la reunión general de inicio de ciclo.', '25/04/2026')
            ]
        )

    conn.commit()
    conn.close()


# Inicializa la base de datos al cargar la aplicación.
init_db()


def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')

@app.route('/oferta')
def oferta():
    return render_template('oferta.html')

@app.route('/costos')
def costos():
    costos_data = query_db('SELECT concepto, precio FROM costos')
    return render_template('costos.html', costos=costos_data)

@app.route('/ubicacion')
def ubicacion():
    return render_template('ubicacion.html', api_key=app.config['GOOGLE_MAPS_API_KEY'])

@app.route('/galeria')
def galeria():
    return render_template('galeria.html')

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        mensaje = request.form.get('mensaje', '').strip()

        if not nombre or not email or not mensaje:
            flash('Por favor completa todos los campos del formulario de contacto.', 'error')
            return redirect(url_for('contacto'))

        flash('Gracias por escribirnos, ' + nombre + '. Te responderemos pronto.', 'success')
        return redirect(url_for('contacto'))

    return render_template('contacto.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']

        if not nombre or not email or not password:
            flash('Por favor complete todos los campos.', 'error')
            return redirect(url_for('registro'))

        hashed_password = generate_password_hash(password)
        try:
            query_db('INSERT INTO users (nombre, email, password) VALUES (?, ?, ?)',
                     (nombre, email, hashed_password))
            flash('Registro exitoso. Inicia sesión para continuar.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('El correo ya está registrado.', 'error')
            return redirect(url_for('registro'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = query_db('SELECT id, nombre, email, password, role FROM users WHERE email = ?', (email,), one=True)

        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['user_role'] = user[4]
            flash('Bienvenido de nuevo, ' + user[1] + '!', 'success')
            return redirect(url_for('dashboard'))

        flash('Correo o contraseña inválidos.', 'error')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Inicia sesión para acceder al contenido exclusivo.', 'error')
        return redirect(url_for('login'))

    avisos = query_db('SELECT titulo, descripcion, fecha FROM avisos ORDER BY id DESC')
    eventos = query_db('SELECT titulo, fecha, descripcion FROM eventos ORDER BY id DESC')
    return render_template('dashboard.html', avisos=avisos, eventos=eventos)


@app.route('/admin')
def admin():
    if session.get('user_role') != 'admin':
        flash('Acceso restringido: sólo administradores.', 'error')
        return redirect(url_for('index'))

    costos = query_db('SELECT id, concepto, precio FROM costos')
    avisos = query_db('SELECT id, titulo, descripcion, fecha FROM avisos ORDER BY id DESC')
    eventos = query_db('SELECT id, titulo, fecha, descripcion FROM eventos ORDER BY id DESC')
    return render_template('admin.html', costos=costos, avisos=avisos, eventos=eventos)


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer as Serializer
import os

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Clave secreta para sesiones
app.secret_key = "advpjsh"

# Configuración de MongoDB Atlas
client = MongoClient("mongodb+srv://angel3663leon:angel06leon@micluster06.8q8rg.mongodb.net/?retryWrites=true&w=majority&appName=MiCluster06")
db = client['db1']
collection = db['Usuarios']

# Configuración de Flask-Mail (Usando Gmail SMTP como ejemplo)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "tu_correo@gmail.com"  # Cambia esto
app.config['MAIL_PASSWORD'] = "tu_contraseña"  # Cambia esto
app.config['MAIL_DEFAULT_SENDER'] = "tu_correo@gmail.com"  # Cambia esto

mail = Mail(app)

# Serializador para crear y verificar tokens
serializer = Serializer(app.secret_key, salt='password-reset-salt')

# Función para enviar correos
def enviar_email(destinatario, asunto, cuerpo):
    try:
        msg = Message(asunto, recipients=[destinatario], html=cuerpo)
        mail.send(msg)
        print(f"Correo enviado con éxito a {destinatario}!")
    except Exception as e:
        print(f"Error al enviar correo: {e}")

@app.route('/')
def home():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', usuario=session['usuario'])

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        usuario = request.form['usuario']
        email = request.form['email']
        contrasena = request.form['contrasena']

        if collection.find_one({'email': email}):
            flash("El correo electrónico ya está registrado.", "error")
            return redirect(url_for('registro'))

        hashed_password = bcrypt.generate_password_hash(contrasena).decode('utf-8')

        collection.insert_one({
            'usuario': usuario,
            'email': email,
            'contrasena': hashed_password
        })
        
        session['usuario'] = usuario
        return redirect(url_for('pagina_principal'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']

        user = collection.find_one({'usuario': usuario})
        
        if user and bcrypt.check_password_hash(user['contrasena'], contrasena):
            session['usuario'] = usuario
            return redirect(url_for('pagina_principal'))
        else:
            flash("Usuario o contraseña incorrectos.", "error")
            return render_template('login.html')

    return render_template('login.html')

@app.route('/pagina_principal')
def pagina_principal():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', usuario=session['usuario'])

@app.route('/mi_perfil')
def mi_perfil():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    usuario = session['usuario']
    user_data = collection.find_one({'usuario': usuario})
    return render_template('mi_perfil.html', usuario=user_data['usuario'], email=user_data['email'])

@app.route('/actualizar_datos', methods=['POST'])
def actualizar_datos():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    usuario = session['usuario']
    nuevos_datos = request.form.to_dict()
    collection.update_one({'usuario': usuario}, {'$set': nuevos_datos})
    
    flash("Tus datos han sido actualizados con éxito.", "success")
    return redirect(url_for('mi_perfil'))

@app.route('/solicitar_prestamo', methods=['GET', 'POST'])
def solicitar_prestamo():
    if request.method == 'POST':
        monto = request.form.get('monto')
        plazo = request.form.get('plazo')

        # Simulación de guardado
        print(f"Solicitud recibida: Monto={monto}, Plazo={plazo}")

        flash("Solicitud enviada con éxito.", "success")  # Mensaje de éxito
        return redirect(url_for('solicitar_prestamo'))  # Redirige después del POST

    return render_template('solicitar_prestamo.html')


@app.route('/revision_solicitudes')
def revision_solicitudes():
    return render_template('revision_solicitudes.html')

@app.route('/notificaciones_solicitudes')
def notificaciones_solicitudes():
    return render_template('notificaciones_solicitudes.html')

@app.route('/realizar_pagos')
def realizar_pagos():
    return render_template('realizar_pagos.html')

@app.route('/visualizar_prestamos')
def visualizar_prestamos():
    return render_template('visualizar_prestamos.html')

@app.route('/recuperar_contrasena', methods=['GET', 'POST'])
def recuperar_contrasena():
    if request.method == 'POST':
        email = request.form['email']
        usuario = collection.find_one({'email': email})

        if usuario:
            token = serializer.dumps(email, salt='password-reset-salt')
            enlace = url_for('restablecer_contrasena', token=token, _external=True)
            asunto = "Recuperación de contraseña"
            cuerpo = f"""
            <p>Hola, hemos recibido una solicitud para restablecer tu contraseña.</p>
            <p>Si no has solicitado este cambio, ignora este mensaje.</p>
            <p>Para restablecer tu contraseña, haz clic en el siguiente enlace:</p>
            <a href="{enlace}">Restablecer contraseña</a>
            """
            enviar_email(email, asunto, cuerpo)
            flash("Te hemos enviado un correo para recuperar tu contraseña.", "success")
        else:
            flash("El correo electrónico no está registrado.", "error")

    return render_template('recuperar_contrasena.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

@app.route('/soporte')
def soporte():
    return render_template('soporte.html')

@app.route('/historial')
def historial():
    return render_template('historial.html')

if __name__ == '__main__':
    app.run(debug=True)

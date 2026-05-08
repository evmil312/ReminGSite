# ReminGSite

Sitio web institucional para Colegio Remington con frontend en HTML/CSS y backend en Flask + SQLite.

## Estructura
- `app.py` - servidor Flask.
- `templates/` - vistas HTML.
- `static/styles.css` - estilos CSS.
- `requirements.txt` - dependencias.

## Cómo ejecutar
1. Instala dependencias:
   ```powershell
   python -m pip install -r requirements.txt
   ```
2. Ejecuta la aplicación:
   ```powershell
   python app.py
   ```
3. Abre `http://127.0.0.1:5000` en tu navegador.

## Usuarios
- Visitantes: acceden a la página pública, costos y ubicación.
- Estudiantes y padres: se registran e inician sesión para ver avisos y calendario.
- Administrador: usa `admin@remingsite.com` con contraseña `admin123`.

## Notas
La primera vez que se ejecuta, se crea `database.db` con datos de ejemplo de costos, eventos y avisos.

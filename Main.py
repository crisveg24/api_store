from flask import Flask, render_template
from controllers.store_controller import store_bp  # Importamos el blueprint para las rutas de Store

# Crear la aplicación Flask
app = Flask(__name__)

# Ruta para la página de inicio (raíz)
@app.route('/')
def home():
    # Renderizar la plantilla index.html para la interfaz de usuario
    return render_template('index.html')  # Asegúrate de tener el archivo index.html en /templates

# Registrar el blueprint de stores
app.register_blueprint(store_bp)

if __name__ == "__main__":
    # Ejecutar la aplicación con el modo debug activado
    app.run(debug=True, host='0.0.0.0', port=5000)  # Especifica un puerto y host en caso de querer usar un entorno diferente

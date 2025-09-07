from flask import Flask
from controllers.store_controller import store_bp  # Importamos el blueprint para las rutas de Store

# Crear la aplicación Flask
app = Flask(__name__)

# Ruta para la página de inicio (raíz)
@app.route('/')
def home():
    return "API de Gestión de Tiendas en funcionamiento", 200

# Registrar el blueprint de stores
app.register_blueprint(store_bp)

if __name__ == "__main__":
    # Ejecutar la aplicación con el modo debug activado
    app.run(debug=True)

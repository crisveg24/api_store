from flask import Blueprint, request, jsonify
from services.store_service import StoreService
from config.database import get_db_session

# Crear el Blueprint para las rutas de Store
store_bp = Blueprint('store_bp', __name__)

# Instancia global de servicio (en producción usar contexto de app o request)
service = StoreService(get_db_session())

@store_bp.route('/stores', methods=['GET'])
def get_stores():
    """
    GET /stores
    Recupera y retorna todas las tiendas registradas en el sistema.
    Utiliza la capa de servicios para obtener la lista completa de tiendas.
    No recibe parámetros.
    Respuesta: JSON con la lista de tiendas.
    """
    try:
        stores = service.listar_tiendas()
        store_list = [s.to_dict() for s in stores]
        return jsonify(store_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@store_bp.route('/stores', methods=['POST'])
def create_store():
    """
    POST /stores
    Crea una nueva tienda.
    Parámetros esperados (JSON):
        store_area (float): Área de la tienda.
        items_available (int): Número de artículos disponibles.
        daily_customer_count (int): Contador de clientes diarios.
        store_sales (float): Ventas diarias de la tienda.
    Respuesta: JSON con los datos de la tienda creada.
    """
    try:
        data = request.get_json()
        store_area = data.get('store_area')
        items_available = data.get('items_available')
        daily_customer_count = data.get('daily_customer_count')
        store_sales = data.get('store_sales')

        if not all([store_area, items_available, daily_customer_count, store_sales]):
            return jsonify({'error': 'Todos los campos son obligatorios'}), 400

        store = service.crear_tienda(store_area, items_available, daily_customer_count, store_sales)
        return jsonify(store.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@store_bp.route('/stores/<int:store_id>', methods=['PUT'])
def update_store(store_id):
    """
    PUT /stores/<store_id>
    Actualiza la información de una tienda existente.
    Parámetros:
        store_id (int): ID de la tienda a actualizar (en la URL).
        store_area (float): Nueva área de la tienda.
        items_available (int): Nuevo número de artículos disponibles.
        daily_customer_count (int): Nuevo contador de clientes diarios.
        store_sales (float): Nuevas ventas diarias de la tienda.
    Respuesta: JSON con los datos de la tienda actualizada o error si no existe.
    """
    try:
        data = request.get_json()
        store_area = data.get('store_area')
        items_available = data.get('items_available')
        daily_customer_count = data.get('daily_customer_count')
        store_sales = data.get('store_sales')

        store = service.actualizar_tienda(store_id, store_area, items_available, daily_customer_count, store_sales)
        if store:
            return jsonify(store.to_dict()), 200
        return jsonify({'error': 'Tienda no encontrada'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@store_bp.route('/stores/<int:store_id>', methods=['DELETE'])
def delete_store(store_id):
    """
    DELETE /stores/<store_id>
    Elimina una tienda específica por su ID.
    Parámetros:
        store_id (int): ID de la tienda a eliminar (en la URL).
    Respuesta: JSON con mensaje de éxito o error si no existe.
    """
    try:
        success = service.eliminar_tienda(store_id)
        if success:
            return jsonify({'message': 'Tienda eliminada'}), 200
        return jsonify({'error': 'Tienda no encontrada'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

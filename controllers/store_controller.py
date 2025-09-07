from flask import Blueprint, request, jsonify
from services.store_service import StoreService
from config.database import get_db_session

store_bp = Blueprint('store_bp', __name__)

# Instancia del servicio
service = StoreService(get_db_session())

@store_bp.route('/stores', methods=['GET'])
def get_stores():
    """
    GET /stores
    Recupera y retorna todas las tiendas registradas en el sistema.
    """
    stores = service.listar_tiendas()
    store_list = [s.to_dict() for s in stores]  # Usamos list comprehension para simplificar
    return jsonify(store_list), 200

@store_bp.route('/stores', methods=['POST'])
def create_store():
    data = request.get_json()
    store_area = data.get('store_area')
    items_available = data.get('items_available')
    daily_customer_count = data.get('daily_customer_count')
    store_sales = data.get('store_sales')

    if not all([store_area, items_available, daily_customer_count, store_sales]):
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400

    store = service.crear_tienda(store_area, items_available, daily_customer_count, store_sales)
    return jsonify(store.to_dict()), 201

@store_bp.route('/stores/<int:store_id>', methods=['GET'])
def get_store(store_id):
    store = service.obtener_tienda(store_id)
    if store:
        return jsonify(store.to_dict()), 200
    return jsonify({'error': 'Tienda no encontrada'}), 404

@store_bp.route('/stores/<int:store_id>', methods=['PUT'])
def update_store(store_id):
    data = request.get_json()
    store_area = data.get('store_area')
    items_available = data.get('items_available')
    daily_customer_count = data.get('daily_customer_count')
    store_sales = data.get('store_sales')

    store = service.actualizar_tienda(store_id, store_area, items_available, daily_customer_count, store_sales)
    if store:
        return jsonify(store.to_dict()), 200
    return jsonify({'error': 'Tienda no encontrada'}), 404

@store_bp.route('/stores/<int:store_id>', methods=['DELETE'])
def delete_store(store_id):
    success = service.eliminar_tienda(store_id)
    if success:
        return jsonify({'message': 'Tienda eliminada'}), 200
    return jsonify({'error': 'Tienda no encontrada'}), 404

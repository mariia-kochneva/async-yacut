from flask import jsonify, request

from . import app
from .services import URLMapService


@app.route('/api/id/', methods=['POST'])
def create_short_link():
    """API: создание короткой ссылки."""
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'message': 'Отсутствует тело запроса'}), 400
    if 'url' not in data:
        return jsonify({'message': '"url" является обязательным полем!'}), 400
    original = data['url']
    custom_id = data.get('custom_id', '') or None
    try:
        url_map = URLMapService.create_short_link(original, custom_id)
        short_link = request.host_url + url_map.short
        return jsonify({
            'url': original,
            'short_link': short_link
        }), 201
    except ValueError as e:
        return jsonify({'message': str(e)}), 400


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original_link(short_id):
    """API: получение оригинальной ссылки по короткому идентификатору."""
    url_map = URLMapService.get_original_url(short_id)
    if url_map is None:
        return jsonify({'message': 'Указанный id не найден'}), 404
    return jsonify({'url': url_map.original}), 200

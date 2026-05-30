import re

from flask import jsonify, request

from . import app, db
from .error_handlers import InvalidAPIUsage
from .models import URLMap
from .utils import get_unique_short_id


@app.route('/api/id/', methods=['POST'])
def create_short_link():
    """API: создание короткой ссылки."""
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'message': 'Отсутствует тело запроса'}), 400
    if 'url' not in data:
        return jsonify({'message': '"url" является обязательным полем!'}), 400
    original = data['url']
    custom_id = data.get('custom_id', '')
    if custom_id:
        if not re.match(r'^[a-zA-Z0-9]+$', custom_id):
            return jsonify(
                {'message': 'Указано недопустимое имя для короткой ссылки'}
            ), 400
        if len(custom_id) > 16:
            return jsonify(
                {'message': 'Указано недопустимое имя для короткой ссылки'}
            ), 400
        if custom_id == 'files':
            return jsonify(
                {'message': 'Указано недопустимое имя для короткой ссылки'}
            ), 400
        if URLMap.query.filter_by(short=custom_id).first():
            return jsonify(
                {
                    'message':
                    'Предложенный вариант короткой ссылки уже существует.'
                }
            ), 400
        short = custom_id
    else:
        short = get_unique_short_id(db.session)
    url_map = URLMap(original=original, short=short)
    db.session.add(url_map)
    db.session.commit()
    short_link = request.host_url + short
    return jsonify({
        'url': original,
        'short_link': short_link
    }), 201


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original_link(short_id):
    """API: получение оригинальной ссылки по короткому идентификатору."""
    url_map = URLMap.query.filter_by(short=short_id).first()
    if url_map is None:
        raise InvalidAPIUsage('Указанный id не найден', 404)
    return jsonify({'url': url_map.original}), 200

from flask import Flask, request, jsonify
from database.db_manager import DBManager
from functools import wraps

app = Flask(__name__)
db = DBManager()

def api_key_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != db.get_setting('api_key', ''):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/users', methods=['GET'])
@api_key_required
def get_users():
    from database.models import SessionLocal, User
    session = SessionLocal()
    users = session.query(User).all()
    result = [{'id': u.id, 'telegram_id': u.telegram_id, 'balance': u.balance, 'purchases': u.total_purchases} for u in users]
    session.close()
    return jsonify(result)

@app.route('/api/products', methods=['GET'])
@api_key_required
def get_products():
    products = db.get_products()
    result = [{'id': p.id, 'name': p.name, 'price': p.price, 'stock': p.stock} for p in products]
    return jsonify(result)

@app.route('/api/stats', methods=['GET'])
@api_key_required
def get_stats():
    stats = db.get_stats()
    return jsonify(stats)

@app.route('/api/user/<int:telegram_id>', methods=['GET'])
@api_key_required
def get_user(telegram_id):
    user = db.get_user(telegram_id)
    if user:
        return jsonify({
            'id': user.id, 'telegram_id': user.telegram_id,
            'balance': user.balance, 'purchases': user.total_purchases,
            'spent': user.total_spent, 'recharged': user.total_recharged
        })
    return jsonify({'error': 'Not found'}), 404

def run_api(port=5000):
    app.run(host='0.0.0.0', port=port, debug=False)

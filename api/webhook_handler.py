from flask import Flask, request, jsonify
from database.db_manager import DBManager
from services.pix_service import PixService
from services.affiliate_service import AffiliateService

app = Flask(__name__)
db = DBManager()

@app.route('/webhook/mercadopago', methods=['POST'])
def mercadopago_webhook():
    data = request.json
    
    if data.get('action') == 'payment.updated':
        payment_id = data.get('data', {}).get('id')
        
        if payment_id:
            ps = PixService()
            result = ps.verificar(payment_id)
            
            if result.get('aprovado'):
                success, total = db.confirm_pix(payment_id)
                
                if success:
                    from database.models import SessionLocal, PixRecharge
                    session = SessionLocal()
                    recharge = session.query(PixRecharge).filter_by(pix_id=payment_id).first()
                    if recharge:
                        af = AffiliateService()
                        af.add_commission(recharge.user_id, total)
                        af.close()
                    session.close()
                    
                    return jsonify({'status': 'ok', 'message': 'Payment confirmed'})
    
    return jsonify({'status': 'received'})

@app.route('/webhook/telegram', methods=['POST'])
def telegram_webhook():
    return jsonify({'status': 'ok'})

@app.route('/webhook/status', methods=['GET'])
def webhook_status():
    return jsonify({
        'status': 'online',
        'timestamp': __import__('datetime').datetime.now().isoformat()
    })

def run_webhook(port=5000):
    app.run(host='0.0.0.0', port=port, debug=False)

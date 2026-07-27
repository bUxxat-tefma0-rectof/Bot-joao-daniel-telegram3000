import requests, uuid, qrcode
from io import BytesIO
from datetime import datetime, timedelta
from config.settings import MP_ACCESS_TOKEN

class PixService:
    def __init__(self): self.token=MP_ACCESS_TOKEN; self.base_url="https://api.mercadopago.com/v1"
    def gerar_pix(self, uid, valor, desc="Recarga", exp_min=15):
        try:
            exp=(datetime.now()+timedelta(minutes=exp_min)).isoformat()
            payload={"transaction_amount":float(valor),"description":desc,"payment_method_id":"pix","payer":{"email":f"user{uid}@bot.com","first_name":"Cliente"},"date_of_expiration":exp}
            headers={"Authorization":f"Bearer {self.token}","Content-Type":"application/json"}
            r=requests.post(f"{self.base_url}/payments",json=payload,headers=headers)
            if r.status_code in [200,201]:
                d=r.json()
                qt=d["point_of_interaction"]["transaction_data"]["qr_code"]
                qr=qrcode.QRCode(version=1,box_size=10,border=2); qr.add_data(qt); qr.make(fit=True)
                img=qr.make_image(fill_color="black",back_color="white"); buf=BytesIO(); img.save(buf,format='PNG'); buf.seek(0)
                return {"sucesso":True,"pix_id":d["id"],"qr_code_imagem":buf,"copia_cola":qt,"expiracao_minutos":exp_min,"valor":valor}
            return {"sucesso":False,"erro":r.text}
        except Exception as e: return {"sucesso":False,"erro":str(e)}
    def verificar(self, pix_id):
        try:
            r=requests.get(f"{self.base_url}/payments/{pix_id}",headers={"Authorization":f"Bearer {self.token}"})
            if r.status_code==200:
                d=r.json(); return {"sucesso":True,"status":d["status"],"aprovado":d["status"]=="approved"}
            return {"sucesso":False}
        except: return {"sucesso":False}

import os
import requests
from dotenv import load_dotenv

# Încărcăm variabilele de mediu
load_dotenv()

BITRIX24_WEBHOOK = os.getenv("BITRIX24_WEBHOOK")

def create_deal(name, phone, email, user_type):
    """ Creează un deal (afacere) în Bitrix24 """
    url = f"{BITRIX24_WEBHOOK}crm.deal.add.json"
    data = {
        "fields": {
            "TITLE": f"Deal - {name}",
            "TYPE_ID": "SALE",
            "STAGE_ID": "NEW",
            "OPENED": "Y",
            "ASSIGNED_BY_ID": 1,  # ID-ul utilizatorului care preia lead-ul
            "UF_CRM_123456": user_type,  # Personalizat, dacă ai nevoie
            "CONTACTS": [{"NAME": name, "PHONE": [{"VALUE": phone}], "EMAIL": [{"VALUE": email}]}]
        }
    }

    response = requests.post(url, json=data)
    result = response.json()

    if "result" in result:
        print(f"✅ Deal creat cu ID: {result['result']}")
        return result["result"]
    else:
        print(f"❌ Eroare la crearea deal-ului: {result}")
        return None

def add_comment_to_deal(deal_id, message):
    """ Adaugă un comentariu în timeline-ul unui deal din Bitrix24 """
    url = f"{BITRIX24_WEBHOOK}crm.timeline.comment.add.json"
    data = {
        "fields": {
            "ENTITY_ID": deal_id,
            "ENTITY_TYPE": "deal",
            "COMMENT": message
        }
    }

    response = requests.post(url, json=data)
    result = response.json()

    if "result" in result:
        print(f"✅ Comentariu adăugat la Deal ID {deal_id}")
    else:
        print(f"❌ Eroare la adăugarea comentariului: {result}")

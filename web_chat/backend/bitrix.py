import os
import requests
from dotenv import load_dotenv

# Încărcăm variabilele de mediu
load_dotenv()

BITRIX24_WEBHOOK = os.getenv("BITRIX24_WEBHOOK")

def create_deal(name, phone, email, source="Web Chat"):
    """ Creează un deal (afacere) în Bitrix24 """
    url = f"{BITRIX24_WEBHOOK}crm.deal.add.json"
    data = {
        "fields": {
            "TITLE": f"Deal - {name}",
            "TYPE_ID": "SALE",
            "STAGE_ID": "NEW",
            "OPENED": "Y",
            "ASSIGNED_BY_ID": 1,  # ID-ul managerului care va prelua lead-ul
            "SOURCE_DESCRIPTION": source,
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

def notify_manager_to_join_chat(deal_id):
    """ Trimite notificare în Bitrix24 doar dacă nu a fost deja trimisă """
    url = f"{BITRIX24_WEBHOOK}crm.timeline.comment.list.json"
    data = {
        "filter": {
            "ENTITY_ID": deal_id,
            "ENTITY_TYPE": "deal"
        },
        "order": {"ID": "DESC"},
        "select": ["COMMENT"]
    }

    response = requests.post(url, json=data)
    result = response.json()

    if "result" in result:
        for comment in result["result"]:
            if "**Un client a inițiat un chat!**" in comment["COMMENT"]:
                print(f"⚠️ Notificarea pentru Deal ID {deal_id} a fost deja trimisă.")
                return  # Oprim trimiterea notificării dacă deja există

    # Dacă nu există notificare, o trimitem acum
    message = f"🔔 **Un client a inițiat un chat!** 🔔\n\n"
    message += f"📌 Deal ID: {deal_id}\n"
    message += f"💬 Pentru a răspunde, folosește secțiunea de comentarii din acest deal."

    data = {
        "fields": {
            "ENTITY_ID": deal_id,
            "ENTITY_TYPE": "deal",
            "COMMENT": message
        }
    }

    response = requests.post(f"{BITRIX24_WEBHOOK}crm.timeline.comment.add.json", json=data)
    result = response.json()

    if "result" in result:
        print(f"✅ Notificare trimisă pentru manager (Deal ID: {deal_id})")
    else:
        print(f"❌ Eroare la trimiterea notificării: {result}")



def get_latest_messages_from_bitrix(deal_id):
    """ Obține ultimele mesaje din Bitrix24 pentru acest deal """
    url = f"{BITRIX24_WEBHOOK}crm.timeline.comment.list.json"
    data = {
        "filter": {
            "ENTITY_ID": deal_id,
            "ENTITY_TYPE": "deal"
        },
        "order": {"ID": "DESC"},
        "select": ["ID", "COMMENT", "CREATED"]
    }

    response = requests.post(url, json=data)
    result = response.json()

    if "result" in result:
        return result["result"]
    else:
        print(f"❌ Eroare la preluarea mesajelor Bitrix24: {result}")
        return []

from sqlalchemy.orm import Session
from models import Contact
import logging

logger = logging.getLogger(__name__)

def create_contact(session: Session, name: str, phone: str) -> dict:
    logger.info(f"[TOOL] create_contact called with name={name}, phone={phone}")
    contact = Contact(name=name, phone=phone)
    session.add(contact)
    session.commit()
    return {"message": f"Added contact {name}.", "contacts": [{"name": name, "phone": phone}]}

def delete_contact(session: Session, name: str) -> dict:
    logger.info(f"[TOOL] delete_contact called with name={name}")
    contact = session.query(Contact).filter_by(name=name).first()
    if contact:
        session.delete(contact)
        session.commit()
        return {"message": f"Deleted contact {name}.", "contacts": [{"name": name, "phone": contact.phone}]}
    else:
        return {"message": f"Contact {name} not found.", "contacts": []}

def update_contact(session: Session, name: str, phone: str) -> dict:
    logger.info(f"[TOOL] update_contact called with name={name}, phone={phone}")
    contact = session.query(Contact).filter_by(name=name).first()
    if contact:
        old_phone = contact.phone
        contact.phone = phone
        session.commit()
        return {"message": f"Updated contact {name} from {old_phone} to {phone}.", "contacts": [{"name": name, "phone": phone}]}
    else:
        return {"message": f"Contact {name} not found.", "contacts": []}
    
def rename_contact(session: Session, old_name: str, new_name: str) -> dict:
    contact = session.query(Contact).filter_by(name=old_name).first()
    if not contact:
        return {
            "message": f"Contact {old_name} not found.",
            "contacts": []
        }
    contact.name = new_name
    session.commit()
    return {
        "message": f"Renamed contact '{old_name}' to '{new_name}'.",
        "contacts": [{"name": new_name, "phone": contact.phone}]
    }

def get_contact(session: Session, name: str) -> dict:
    logger.info(f"[TOOL] get_contact called with name={name}")
    contact = session.query(Contact).filter_by(name=name).first()
    if contact:
        return {"message": f"{contact.name}'s phone number is {contact.phone}.", "contacts": [{"name": contact.name, "phone": contact.phone}]}
    else:
        return {"message": f"Contact {name} not found.", "contacts": []}

def list_contacts(session: Session) -> dict:
    logger.info("[TOOL] list_contacts called")
    contacts = session.query(Contact).all()
    contacts_list = [{"name": c.name, "phone": c.phone} for c in contacts]
    if contacts_list:
        msg = "Here are all your contacts."
    else:
        msg = "Your phone book is empty."
    return {"message": msg, "contacts": contacts_list}

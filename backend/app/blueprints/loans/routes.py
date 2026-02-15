from datetime import datetime, date
from flask import request
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.emprunt import Emprunt
from app.models.livre import Livre
from app.models.membre import Membre
from . import loans_bp


def ok(data, status=200):
    return data, status


def err(message, status=400, details=None):
    payload = {"error": message}
    if details is not None:
        payload["details"] = details
    return payload, status


def get_json():
    return request.get_json(silent=True) or {}


def parse_date(value, field_name: str) -> date | None:
    """
    Accepts:
      - None -> None
      - "" -> None
      - "YYYY-MM-DD" -> date
    Raises ValueError if invalid
    """
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    return datetime.strptime(value, "%Y-%m-%d").date()


def serialize_emprunt(e: Emprunt):
    return {
        "id_emprunt": e.id_emprunt,
        "livre_id": e.livre_id,
        "membre_id": e.membre_id,
        "date_emprunt": e.date_emprunt.isoformat() if e.date_emprunt else None,
        "date_retour": e.date_retour.isoformat() if e.date_retour else None,
        # optional embedded info (handy for React)
        "livre": {
            "id_livre": e.livre.id_livre,
            "titre": e.livre.titre,
            "isbn": e.livre.isbn,
        } if getattr(e, "livre", None) else None,
        "membre": {
            "id_mbre": e.membre.id_mbre,
            "nom_mbre": e.membre.nom_mbre,
            "prenom_mbre": e.membre.prenom_mbre,
            "email_mbre": e.membre.email_mbre,
        } if getattr(e, "membre", None) else None,
    }


# -------------------------
# GET /api/loans
# -------------------------
@loans_bp.get("/")
def list_emprunts():
    emprunts = Emprunt.query.order_by(Emprunt.id_emprunt.asc()).all()
    return ok([serialize_emprunt(e) for e in emprunts])


# -------------------------
# POST /api/loans
# Create a loan + decrement livre.quantite
# -------------------------
@loans_bp.post("/")
def create_emprunt():
    data = get_json()

    required = ["livre_id", "membre_id", "date_emprunt"]
    if not all(k in data for k in required):
        return err("Champs obligatoires manquants", details={"required": required})

    try:
        livre_id = int(data["livre_id"])
        membre_id = int(data["membre_id"])
        d_emprunt = parse_date(data["date_emprunt"], "date_emprunt")
        d_retour = parse_date(data.get("date_retour"), "date_retour")

        if d_emprunt is None:
            return err("date_emprunt is required")

        # Validate FK existence
        livre = Livre.query.get(livre_id)
        if not livre:
            return err("ID livre inexistant", 400)

        membre = Membre.query.get(membre_id)
        if not membre:
            return err("ID membre inexistant", 400)

        # Business rule: must have stock
        if (livre.quantite or 0) <= 0:
            return err("Aucune quantité disponible pour ce livre", 400)

        # If the loan is created already returned (date_retour provided),
        # we won't decrement stock (optional policy).
        # Most libraries: a returned loan should not affect stock.
        decrement_stock = d_retour is None

        new_emprunt = Emprunt(
            livre_id=livre_id,
            membre_id=membre_id,
            date_emprunt=d_emprunt,
            date_retour=d_retour,
        )

        db.session.add(new_emprunt)

        if decrement_stock:
            livre.quantite = (livre.quantite or 0) - 1

        db.session.commit()
        return ok(serialize_emprunt(new_emprunt), 201)

    except ValueError:
        db.session.rollback()
        return err("Format invalide (ID entier, date YYYY-MM-DD)")
    except IntegrityError as e:
        db.session.rollback()
        return err("Erreur d'intégrité (contrainte DB)", details=str(e.orig))
    except Exception as e:
        db.session.rollback()
        return err("Erreur serveur", 500, details=str(e))


# -------------------------
# PUT /api/loans/<id>
# Update loan safely
# (Does NOT modify stock automatically)
# -------------------------
@loans_bp.put("/<int:emprunt_id>")
def update_emprunt(emprunt_id: int):
    e = Emprunt.query.get(emprunt_id)
    if not e:
        return err("Emprunt introuvable", 404)

    data = get_json()

    try:
        # If you change livre_id or membre_id, validate existence
        if "livre_id" in data:
            new_livre_id = int(data["livre_id"])
            livre = Livre.query.get(new_livre_id)
            if not livre:
                return err("ID livre inexistant")
            e.livre_id = new_livre_id

        if "membre_id" in data:
            new_membre_id = int(data["membre_id"])
            membre = Membre.query.get(new_membre_id)
            if not membre:
                return err("ID membre inexistant")
            e.membre_id = new_membre_id

        if "date_emprunt" in data:
            d_emprunt = parse_date(data["date_emprunt"], "date_emprunt")
            if d_emprunt is None:
                return err("date_emprunt cannot be empty")
            e.date_emprunt = d_emprunt

        if "date_retour" in data:
            e.date_retour = parse_date(data["date_retour"], "date_retour")

        db.session.commit()
        return ok(serialize_emprunt(e))

    except ValueError:
        db.session.rollback()
        return err("ID ou date invalide (YYYY-MM-DD)")
    except IntegrityError as ex:
        db.session.rollback()
        return err("Erreur d'intégrité (contrainte DB)", details=str(ex.orig))
    except Exception as ex:
        db.session.rollback()
        return err("Erreur serveur", 500, details=str(ex))

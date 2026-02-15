from datetime import date
from flask import request
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.models.profil import Profil
from app.models.membre import Membre
from app.models.utilisateur import Utilisateur
from . import users_bp


def ok(data, status=200):
    return data, status


def err(message, status=400, details=None):
    payload = {"error": message}
    if details is not None:
        payload["details"] = details
    return payload, status


def get_json():
    return request.get_json(silent=True) or {}


def serialize_profil(p: Profil):
    return {
        "id_profil": p.id_profil,
        "nom_p": p.nom_p,
        "description_p": p.description_p,
    }


def serialize_membre(m: Membre):
    return {
        "id_mbre": m.id_mbre,
        "nom_mbre": m.nom_mbre,
        "prenom_mbre": m.prenom_mbre,
        "email_mbre": m.email_mbre,
        "date_adhesion": m.date_adhesion.isoformat() if m.date_adhesion else None,
    }


def serialize_utilisateur(u: Utilisateur):
    return {
        "id_user": u.id_user,
        "login": u.login,
        "profil_id": u.profil_id,
        "mbre_id": u.mbre_id,
        "profil": serialize_profil(u.profil) if u.profil else None,
        "membre": serialize_membre(u.membre) if u.membre else None,
    }


# -----------------------
# PROFILS (roles)
# -----------------------

@users_bp.get("/profils")
def list_profils():
    profils = Profil.query.order_by(Profil.id_profil.desc()).all()
    return ok([serialize_profil(p) for p in profils])


@users_bp.post("/profils")
def create_profil():
    data = get_json()
    nom_p = data.get("nom_p")
    description_p = data.get("description_p")

    if not nom_p:
        return err("nom_p is required")

    p = Profil(nom_p=nom_p, description_p=description_p)
    db.session.add(p)
    db.session.commit()
    return ok(serialize_profil(p), 201)


@users_bp.put("/profils/<int:profil_id>")
def update_profil(profil_id: int):
    p = Profil.query.get(profil_id)
    if not p:
        return err("Profil not found", 404)

    data = get_json()
    if "nom_p" in data:
        if not data["nom_p"]:
            return err("nom_p cannot be empty")
        p.nom_p = data["nom_p"]
    if "description_p" in data:
        p.description_p = data["description_p"]

    db.session.commit()
    return ok(serialize_profil(p))


@users_bp.delete("/profils/<int:profil_id>")
def delete_profil(profil_id: int):
    p = Profil.query.get(profil_id)
    if not p:
        return err("Profil not found", 404)

    db.session.delete(p)
    db.session.commit()
    return ok({"status": "deleted"})


# -----------------------
# MEMBRES
# -----------------------

@users_bp.get("/members")
def list_members():
    members = Membre.query.order_by(Membre.id_mbre.desc()).all()
    return ok([serialize_membre(m) for m in members])


@users_bp.get("/members/<int:membre_id>")
def get_member(membre_id: int):
    m = Membre.query.get(membre_id)
    if not m:
        return err("Member not found", 404)
    return ok(serialize_membre(m))


@users_bp.post("/members")
def create_member():
    data = get_json()
    nom = data.get("nom_mbre")
    prenom = data.get("prenom_mbre")
    email = data.get("email_mbre")
    date_str = data.get("date_adhesion")  # "YYYY-MM-DD" optional

    if not nom or not prenom or not email:
        return err("nom_mbre, prenom_mbre, email_mbre are required")

    d = None
    if date_str:
        try:
            d = date.fromisoformat(date_str)
        except ValueError:
            return err("date_adhesion must be YYYY-MM-DD")

    m = Membre(nom_mbre=nom, prenom_mbre=prenom, email_mbre=email, date_adhesion=d)
    db.session.add(m)
    db.session.commit()
    return ok(serialize_membre(m), 201)


@users_bp.put("/members/<int:membre_id>")
def update_member(membre_id: int):
    m = Membre.query.get(membre_id)
    if not m:
        return err("Member not found", 404)

    data = get_json()

    if "nom_mbre" in data:
        m.nom_mbre = data["nom_mbre"]
    if "prenom_mbre" in data:
        m.prenom_mbre = data["prenom_mbre"]
    if "email_mbre" in data:
        m.email_mbre = data["email_mbre"]

    if "date_adhesion" in data:
        date_str = data["date_adhesion"]
        if date_str is None or date_str == "":
            m.date_adhesion = None
        else:
            try:
                m.date_adhesion = date.fromisoformat(date_str)
            except ValueError:
                return err("date_adhesion must be YYYY-MM-DD")

    db.session.commit()
    return ok(serialize_membre(m))


@users_bp.delete("/members/<int:membre_id>")
def delete_member(membre_id: int):
    m = Membre.query.get(membre_id)
    if not m:
        return err("Member not found", 404)

    db.session.delete(m)
    db.session.commit()
    return ok({"status": "deleted"})


# -----------------------
# UTILISATEURS (accounts)
# -----------------------

@users_bp.get("/accounts")
def list_accounts():
    accounts = Utilisateur.query.order_by(Utilisateur.id_user.desc()).all()
    return ok([serialize_utilisateur(u) for u in accounts])


@users_bp.post("/accounts")
def create_account():
    """
    JSON:
    {
      "login": "admin",
      "password": "secret",
      "profil_id": 1,
      "mbre_id": 2   // optional
    }
    """
    data = get_json()
    login = data.get("login")
    password = data.get("password")
    profil_id = data.get("profil_id")
    mbre_id = data.get("mbre_id")

    if not login or not password:
        return err("login and password are required")
    if profil_id is None:
        return err("profil_id is required")

    profil = Profil.query.get(profil_id)
    if not profil:
        return err("profil_id does not exist")

    if mbre_id is not None:
        membre = Membre.query.get(mbre_id)
        if not membre:
            return err("mbre_id does not exist")

    hashed = generate_password_hash(password)

    u = Utilisateur(login=login, password=hashed, profil_id=profil_id, mbre_id=mbre_id)
    db.session.add(u)

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return err("Integrity error (duplicate login?)", details=str(e.orig))

    return ok(serialize_utilisateur(u), 201)


@users_bp.put("/accounts/<int:user_id>")
def update_account(user_id: int):
    u = Utilisateur.query.get(user_id)
    if not u:
        return err("Account not found", 404)

    data = get_json()

    if "login" in data:
        if not data["login"]:
            return err("login cannot be empty")
        u.login = data["login"]

    if "password" in data:
        if not data["password"]:
            return err("password cannot be empty")
        u.password = generate_password_hash(data["password"])

    if "profil_id" in data:
        profil = Profil.query.get(data["profil_id"])
        if not profil:
            return err("profil_id does not exist")
        u.profil_id = data["profil_id"]

    if "mbre_id" in data:
        mbre_id = data["mbre_id"]
        if mbre_id is None:
            u.mbre_id = None
        else:
            membre = Membre.query.get(mbre_id)
            if not membre:
                return err("mbre_id does not exist")
            u.mbre_id = mbre_id

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return err("Integrity error", details=str(e.orig))

    return ok(serialize_utilisateur(u))


@users_bp.delete("/accounts/<int:user_id>")
def delete_account(user_id: int):
    u = Utilisateur.query.get(user_id)
    if not u:
        return err("Account not found", 404)

    db.session.delete(u)
    db.session.commit()
    return ok({"status": "deleted"})


# -----------------------
# AUTH (simple login)
# -----------------------

@users_bp.post("/login")
def login():
    """
    JSON: { "login": "...", "password": "..." }
    Returns user info if OK.
    (No JWT here to keep it simple; you can add later.)
    """
    data = get_json()
    login = data.get("login")
    password = data.get("password")

    if not login or not password:
        return err("login and password are required")

    u = Utilisateur.query.filter_by(login=login).first()
    if not u:
        return err("Invalid credentials", 401)

    if not check_password_hash(u.password, password):
        return err("Invalid credentials", 401)

    return ok({"message": "login_ok", "user": serialize_utilisateur(u)})

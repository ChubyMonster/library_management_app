from flask import request
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models.categorie import Categorie
from app.models.auteur import Auteur
from app.models.livre import Livre


def ok(data, status=200):
    return data, status


def err(message, status=400, details=None):
    payload = {"error": message}
    if details is not None:
        payload["details"] = details
    return payload, status


def get_json():
    return request.get_json(silent=True) or {}


def serialize_category(c: Categorie):
    return {"id_cat": c.id_cat, "nom_cat": c.nom_cat, "champ": c.champ}


def serialize_author(a: Auteur):
    return {"id_auteur": a.id_auteur, "nom_auteur": a.nom_auteur, "prenom_auteur": a.prenom_auteur}


def serialize_book(b: Livre):
    return {
        "id_livre": b.id_livre,
        "isbn": b.isbn,
        "titre": b.titre,
        "quantite": b.quantite,
        "cat_id": b.cat_id,
        "categorie": serialize_category(b.categorie) if b.categorie else None,
        "auteurs": [serialize_author(a) for a in (b.auteurs or [])],
    }


# -----------------------
# CATEGORIES
# -----------------------

from . import books_bp


@books_bp.get("/categories")
def list_categories():
    cats = Categorie.query.order_by(Categorie.id_cat.desc()).all()
    return ok([serialize_category(c) for c in cats])


@books_bp.post("/categories")
def create_category():
    data = get_json()
    nom_cat = data.get("nom_cat")
    champ = data.get("champ")

    if not nom_cat:
        return err("nom_cat is required")

    c = Categorie(nom_cat=nom_cat, champ=champ)
    db.session.add(c)
    db.session.commit()
    return ok(serialize_category(c), 201)


@books_bp.put("/categories/<int:cat_id>")
def update_category(cat_id: int):
    c = Categorie.query.get(cat_id)
    if not c:
        return err("Category not found", 404)

    data = get_json()
    if "nom_cat" in data:
        c.nom_cat = data["nom_cat"]
    if "champ" in data:
        c.champ = data["champ"]

    db.session.commit()
    return ok(serialize_category(c))


@books_bp.delete("/categories/<int:cat_id>")
def delete_category(cat_id: int):
    c = Categorie.query.get(cat_id)
    if not c:
        return err("Category not found", 404)

    db.session.delete(c)
    db.session.commit()
    return ok({"status": "deleted"})


# -----------------------
# AUTHORS
# -----------------------

@books_bp.get("/authors")
def list_authors():
    authors = Auteur.query.order_by(Auteur.id_auteur.desc()).all()
    return ok([serialize_author(a) for a in authors])


@books_bp.post("/authors")
def create_author():
    data = get_json()
    nom = data.get("nom_auteur")
    prenom = data.get("prenom_auteur")

    if not nom or not prenom:
        return err("nom_auteur and prenom_auteur are required")

    a = Auteur(nom_auteur=nom, prenom_auteur=prenom)
    db.session.add(a)
    db.session.commit()
    return ok(serialize_author(a), 201)


@books_bp.put("/authors/<int:author_id>")
def update_author(author_id: int):
    a = Auteur.query.get(author_id)
    if not a:
        return err("Author not found", 404)

    data = get_json()
    if "nom_auteur" in data:
        a.nom_auteur = data["nom_auteur"]
    if "prenom_auteur" in data:
        a.prenom_auteur = data["prenom_auteur"]

    db.session.commit()
    return ok(serialize_author(a))


@books_bp.delete("/authors/<int:author_id>")
def delete_author(author_id: int):
    a = Auteur.query.get(author_id)
    if not a:
        return err("Author not found", 404)

    db.session.delete(a)
    db.session.commit()
    return ok({"status": "deleted"})


# -----------------------
# BOOKS
# -----------------------

@books_bp.get("/books")
def list_books():
    """
    Optional query params:
      - catId=int
      - q=str (search in titre, isbn, author name)
    """
    cat_id = request.args.get("catId", type=int)
    q = (request.args.get("q") or "").strip()

    query = Livre.query

    if cat_id:
        query = query.filter(Livre.cat_id == cat_id)

    if q:
        like = f"%{q}%"
        # join authors so searching author works
        query = query.outerjoin(Livre.auteurs).filter(
            or_(
                Livre.titre.ilike(like),
                Livre.isbn.ilike(like),
                Auteur.nom_auteur.ilike(like),
                Auteur.prenom_auteur.ilike(like),
            )
        ).distinct()

    books = query.order_by(Livre.id_livre.desc()).all()
    return ok([serialize_book(b) for b in books])


@books_bp.get("/books/<int:book_id>")
def get_book(book_id: int):
    b = Livre.query.get(book_id)
    if not b:
        return err("Book not found", 404)
    return ok(serialize_book(b))


@books_bp.post("/books")
def create_book():
    """
    JSON:
    {
      "titre": "...",
      "isbn": "...",
      "quantite": 3,
      "cat_id": 1,
      "auteur_ids": [1,2]
    }
    """
    data = get_json()
    titre = data.get("titre")
    isbn = data.get("isbn")
    quantite = data.get("quantite", 1)
    cat_id = data.get("cat_id")
    auteur_ids = data.get("auteur_ids") or []

    if not titre:
        return err("titre is required")
    if cat_id is None:
        return err("cat_id is required")
    if not isinstance(quantite, int) or quantite < 0:
        return err("quantite must be a non-negative integer")

    cat = Categorie.query.get(cat_id)
    if not cat:
        return err("cat_id does not exist")

    auteurs = []
    if auteur_ids:
        auteurs = Auteur.query.filter(Auteur.id_auteur.in_(auteur_ids)).all()
        found = {a.id_auteur for a in auteurs}
        missing = [i for i in auteur_ids if i not in found]
        if missing:
            return err("Some auteur_ids do not exist", details={"missing_ids": missing})

    b = Livre(titre=titre, isbn=isbn, quantite=quantite, cat_id=cat_id)
    b.auteurs = auteurs
    db.session.add(b)

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return err("Integrity error (maybe duplicate ISBN?)", details=str(e.orig))

    return ok(serialize_book(b), 201)


@books_bp.put("/books/<int:book_id>")
def update_book(book_id: int):
    """
    You can update any field + replace authors:
    {
      "titre": "...",
      "isbn": "...",
      "quantite": 5,
      "cat_id": 2,
      "auteur_ids": [3,4]
    }
    """
    b = Livre.query.get(book_id)
    if not b:
        return err("Book not found", 404)

    data = get_json()

    if "titre" in data:
        if not data["titre"]:
            return err("titre cannot be empty")
        b.titre = data["titre"]

    if "isbn" in data:
        b.isbn = data["isbn"]

    if "quantite" in data:
        qte = data["quantite"]
        if not isinstance(qte, int) or qte < 0:
            return err("quantite must be a non-negative integer")
        b.quantite = qte

    if "cat_id" in data:
        new_cat = Categorie.query.get(data["cat_id"])
        if not new_cat:
            return err("cat_id does not exist")
        b.cat_id = data["cat_id"]

    if "auteur_ids" in data:
        auteur_ids = data.get("auteur_ids") or []
        auteurs = []
        if auteur_ids:
            auteurs = Auteur.query.filter(Auteur.id_auteur.in_(auteur_ids)).all()
            found = {a.id_auteur for a in auteurs}
            missing = [i for i in auteur_ids if i not in found]
            if missing:
                return err("Some auteur_ids do not exist", details={"missing_ids": missing})
        b.auteurs = auteurs

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return err("Integrity error", details=str(e.orig))

    return ok(serialize_book(b))


@books_bp.delete("/books/<int:book_id>")
def delete_book(book_id: int):
    b = Livre.query.get(book_id)
    if not b:
        return err("Book not found", 404)

    db.session.delete(b)
    db.session.commit()
    return ok({"status": "deleted"})

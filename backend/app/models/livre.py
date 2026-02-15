from app.extensions import db
from .auteur import Livre_Auteur

class Livre(db.Model):
    __tablename__ = "livre"

    id_livre = db.Column("id_livre", db.Integer, primary_key=True)
    isbn = db.Column("isbn", db.String(20))
    titre = db.Column("titre", db.String(255))
    quantite = db.Column("quantite", db.Integer)

    cat_id = db.Column("cat_id", db.Integer, db.ForeignKey("categorie.id_cat"))
    categorie = db.relationship("Categorie")

    auteurs = db.relationship("Auteur", secondary=Livre_Auteur, backref="livres")

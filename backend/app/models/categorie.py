from app.extensions import db

class Categorie(db.Model):
    __tablename__ = "categorie"

    id_cat = db.Column("id_cat", db.Integer, primary_key=True)
    nom_cat = db.Column("nom_cat", db.String(100))
    champ = db.Column("champ", db.String(100))

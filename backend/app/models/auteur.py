from app.extensions import db

Livre_Auteur = db.Table(
    "livre_auteur",
    db.Column("livre_id", db.Integer, db.ForeignKey("livre.id_livre"), primary_key=True),
    db.Column("auteur_id", db.Integer, db.ForeignKey("auteur.id_auteur"), primary_key=True),
)

class Auteur(db.Model):
    __tablename__ = "auteur"

    id_auteur = db.Column("id_auteur", db.Integer, primary_key=True)
    nom_auteur = db.Column("nom_auteur", db.String(100))
    prenom_auteur = db.Column("prenom_auteur", db.String(100))

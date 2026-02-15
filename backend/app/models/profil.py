from app.extensions import db

class Profil(db.Model):
    __tablename__ = "profil"

    id_profil = db.Column("id_profil", db.Integer, primary_key=True)
    nom_p = db.Column("nom_p", db.String(100), nullable=False)
    description_p = db.Column("description_p", db.String(255), nullable=True)

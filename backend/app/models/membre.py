from app.extensions import db

class Membre(db.Model):
    __tablename__ = "membre"

    id_mbre = db.Column("id_mbre", db.Integer, primary_key=True)
    nom_mbre = db.Column("nom_mbre", db.String(100))
    prenom_mbre = db.Column("prenom_mbre", db.String(100))
    email_mbre = db.Column("email_mbre", db.String(100))
    date_adhesion = db.Column("date_adhesion", db.Date)

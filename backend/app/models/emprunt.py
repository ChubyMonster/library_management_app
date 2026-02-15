from app.extensions import db

class Emprunt(db.Model):
    __tablename__ = "emprunt"

    id_emprunt = db.Column("id_emprunt", db.Integer, primary_key=True)

    livre_id = db.Column("livre_id", db.Integer, db.ForeignKey("livre.id_livre"))
    membre_id = db.Column("membre_id", db.Integer, db.ForeignKey("membre.id_mbre"))

    date_emprunt = db.Column("date_emprunt", db.Date)
    date_retour = db.Column("date_retour", db.Date)

    livre = db.relationship("Livre")
    membre = db.relationship("Membre")

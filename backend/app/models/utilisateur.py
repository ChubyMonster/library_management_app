from app.extensions import db

class Utilisateur(db.Model):
    __tablename__ = "utilisateur"

    id_user = db.Column("id_user", db.Integer, primary_key=True)
    login = db.Column("login", db.String(100))
    password = db.Column("password", db.String(100))

    profil_id = db.Column("profil_id", db.Integer, db.ForeignKey("profil.id_profil"))
    # If you add the FK in SQL:
    mbre_id = db.Column("mbre_id", db.Integer, db.ForeignKey("membre.id_mbre"), nullable=True)

    profil = db.relationship("Profil")
    membre = db.relationship("Membre")

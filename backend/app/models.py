# backend/app/models.py
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), default='user', nullable=False)

    # Adiciona a relação com OwnedCharacter.
    # 'backref' permite acessar o objeto User a partir de OwnedCharacter (owned_char.owner).
    # 'lazy=True' significa que os dados de OwnedCharacter serão carregados apenas quando acessados.
    owned_characters_association = db.relationship(
        # <-- NOVA RELAÇÃO
        'OwnedCharacter', backref='owner', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"User('{self.username}', '{self.id}', '{self.role}')"

    def set_password(self, password):
        """Define a senha do usuário, gerando um hash seguro."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se a senha fornecida corresponde ao hash armazenado."""
        return check_password_hash(self.password_hash, password)

    def has_role(self, required_role):
        return self.role == required_role

    def is_admin(self):
        return self.role == 'admin'


# NOVO MODELO: Para armazenar personagens possuídos por um usuário
class OwnedCharacter(db.Model):
    # Chave primária composta para garantir a unicidade de (user_id, character_id)
    # <-- Chave estrangeira para User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    # <-- ID do personagem (deve corresponder aos IDs dos seus JSONs)
    character_id = db.Column(db.String(50), primary_key=True)

    def __repr__(self):
        return f"<OwnedCharacter UserID: {self.user_id}, CharID: {self.character_id}>"

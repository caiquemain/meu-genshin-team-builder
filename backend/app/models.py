# backend/app/models.py
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from typing import Dict, Optional  # <-- Importe Optional para type hints
import json  # <-- Importar json para serializacao/deserializacao


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), default='user', nullable=False)

    owned_characters_association = db.relationship(
        'OwnedCharacter', backref='owner', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"User('{self.username}', '{self.id}', '{self.role}')"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, required_role):
        return self.role == required_role

    def is_admin(self):
        return self.role == 'admin'


class OwnedCharacter(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    character_id = db.Column(db.String(50), primary_key=True)

    def __repr__(self):
        return f"<OwnedCharacter UserID: {self.user_id}, CharID: {self.character_id}>"

# TierListEntry para armazenar os dados raspados da Tier List


# TierListEntry para armazenar os dados raspados da Tier List
class TierListEntry(db.Model):
    character_id = db.Column(db.String(50), primary_key=True, unique=True)
    character_name = db.Column(db.String(100), nullable=False)
    tier_level = db.Column(db.String(10), nullable=False)
    # Aumentar o tamanho para strings longas de roles
    role = db.Column(db.String(255), nullable=False)
    constellation = db.Column(db.String(10))
    rarity = db.Column(db.Integer)
    element = db.Column(db.String(20), nullable=False)
    # NOVO: Colunas para armazenar a nota agregada e a contagem de fontes
    average_numeric_tier = db.Column(db.Float)  # Float para a media
    sources_contributing = db.Column(db.Integer)  # Integer para a contagem
    # Coluna para armazenar original_scores_by_site como JSON string
    original_scores_by_site_json = db.Column(db.Text)

    # MÉTODO __init__ explícito com Type Hints para satisfazer o Pylance
    def __init__(self, character_id: str, character_name: str, tier_level: str, role: str,
                 constellation: Optional[str] = None, rarity: Optional[int] = None, element: Optional[str] = None,
                 # NOVO ARGUMENTO
                 average_numeric_tier: Optional[float] = None,
                 sources_contributing: Optional[int] = None,  # NOVO ARGUMENTO
                 original_scores_by_site: Optional[Dict[str, str]] = None):
        self.character_id = character_id
        self.character_name = character_name
        self.tier_level = tier_level
        self.role = role
        self.constellation = constellation
        self.rarity = rarity
        self.element = element
        self.average_numeric_tier = average_numeric_tier  # ATRIBUIR
        self.sources_contributing = sources_contributing  # ATRIBUIR
        self.original_scores_by_site_json = json.dumps(
            original_scores_by_site) if original_scores_by_site else "{}"

    # Propriedade para acessar o dicionário de scores (deserializa o JSON)
    @property
    def original_scores_by_site(self) -> Dict[str, str]:
        if self.original_scores_by_site_json:
            return json.loads(self.original_scores_by_site_json)
        return {}

    def __repr__(self):
        return f"<TierListEntry {self.character_name} ({self.character_id}) - Tier: {self.tier_level} - Role: {self.role}>"

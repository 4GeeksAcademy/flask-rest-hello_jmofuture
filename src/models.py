from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


favorite_planets_association = db.Table(
    'favorite_planets', db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('planet_id', db.Integer, db.ForeignKey('planets.id'), primary_key=True)
)


favorite_characters_association = db.Table(
    'favorite_characters', db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('character_id', db.Integer, db.ForeignKey('characters.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    favorite_planets = db.relationship('Planet', secondary=favorite_planets_association, back_populates='favorited_by')
    favorite_characters = db.relationship('Character', secondary=favorite_characters_association, back_populates='favorited_by')

    def __repr__(self):
        return f'<User {self.email}>'

    def serialize(self):
        excluded_fields = {"password", "_sa_instance_state"}
        return {
            key: getattr(self, key)
            for key in self.__dict__
            if key not in excluded_fields
        }


class Planet(db.Model):
    __tablename__ = 'planets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    climate = db.Column(db.String(100))
    terrain = db.Column(db.String(100))

    favorited_by = db.relationship('User', secondary=favorite_planets_association, back_populates='favorite_planets')

    def __repr__(self):
        return f'<Planet {self.name}>'

    def serialize(self):
        return {
            key: getattr(self, key)
            for key in self.__dict__
        }


class Character(db.Model):
    __tablename__ = 'characters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    height = db.Column(db.String(50))
    mass = db.Column(db.String(50))

    favorited_by = db.relationship('User', secondary=favorite_characters_association, back_populates='favorite_characters')

    def __repr__(self):
        return f'<Character {self.name}>'

    def serialize(self):
        return {
            key: getattr(self, key)
            for key in self.__dict__
        }

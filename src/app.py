"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


@app.route('/people', methods=['GET'])
def get_all_characters():
    characters = Character.query.all()
    if not characters:
        return jsonify({'msg': 'No se encontraron personajes'}), 404
    return jsonify([character.serialize() for character in characters]), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_character_by_id(people_id):
    character = Character.query.get(people_id)
    if not character:
        return jsonify({'msg': f'Personaje con ID {people_id} no encontrado'}), 404
    return jsonify(character.serialize()), 200


@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    if not planets:
        return jsonify({'msg': 'No se encontraron planetas'}), 404
    return jsonify([planet.serialize() for planet in planets]), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({'msg': f'Planeta con ID {planet_id} no encontrado'}), 404
    return jsonify(planet.serialize()), 200


@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    if not users:
        return jsonify({'msg': 'No se encontraron usuarios'}), 404
    return jsonify([user.serialize() for user in users]), 200


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    current_user_id = 1
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'msg': 'Usuario no encontrado'}), 404
    return jsonify({
        'favorite_planets': [planet.serialize() for planet in user.favorite_planets],
        'favorite_characters': [character.serialize() for character in user.favorite_characters]
    }), 200


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    current_user_id = 1
    user = User.query.get(current_user_id)
    planet = Planet.query.get(planet_id)
    if not user or not planet:
        return jsonify({'msg': 'Usuario o planeta no encontrado'}), 404
    user.favorite_planets.append(planet)
    db.session.commit()
    return jsonify({'msg': f'Planeta {planet.name} añadido a favoritos'}), 200

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_character(people_id):
    current_user_id = 1
    user = User.query.get(current_user_id)
    character = Character.query.get(people_id)
    if not user or not character:
        return jsonify({'msg': 'Usuario o personaje no encontrado'}), 404
    user.favorite_characters.append(character)
    db.session.commit()
    return jsonify({'msg': f'Personaje {character.name} añadido a favoritos'}), 200


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    current_user_id = 1
    user = User.query.get(current_user_id)
    planet = Planet.query.get(planet_id)
    if not user or not planet:
        return jsonify({'msg': 'Usuario o planeta no encontrado'}), 404
    if planet in user.favorite_planets:
        user.favorite_planets.remove(planet)
        db.session.commit()
        return jsonify({'msg': f'Planeta {planet.name} eliminado de favoritos'}), 200
    return jsonify({'msg': f'El planeta no estaba en los favoritos del usuario'}), 404


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_character(people_id):
    current_user_id = 1
    user = User.query.get(current_user_id)
    character = Character.query.get(people_id)
    if not user or not character:
        return jsonify({'msg': 'Usuario o personaje no encontrado'}), 404
    if character in user.favorite_characters:
        user.favorite_characters.remove(character)
        db.session.commit()
        return jsonify({'msg': f'Personaje {character.name} eliminado de favoritos'}), 200
    return jsonify({'msg': f'El personaje no estaba en los favoritos del usuario'}), 404


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

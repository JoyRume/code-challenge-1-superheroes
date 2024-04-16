#!/usr/bin/env python3

from flask import Flask, request, make_response,jsonify,request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'



@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    serialized_heroes = [hero.to_dict(only=('id', 'name', 'super_name')) for hero in heroes]
    return jsonify(serialized_heroes)


@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero_by_id(id):
    hero = Hero.query.get(id)
    if hero is None:
        return jsonify({"error": "Hero not found"}), 404
    
    serialized_hero = {
        "id": hero.id,
        "name": hero.name,
        "super_name": hero.super_name,
        "hero_powers": []
    }
    
    for hero_power in hero.hero_powers:
        serialized_hero_power = {
            "id": hero_power.id,
            "hero_id": hero_power.hero_id,
            "power_id": hero_power.power_id,
            "strength": hero_power.strength,
            "power": {
                "id": hero_power.power.id,
                "name": hero_power.power.name,
                "description": hero_power.power.description
            }
        }
        serialized_hero["hero_powers"].append(serialized_hero_power)
    
    return jsonify(serialized_hero)

# powers
@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    serialized_powers = [{
        "id": power.id,
        "name": power.name,
        "description": power.description
    } for power in powers]
    return jsonify(serialized_powers)

@app.route('/powers/<int:id>', methods=['GET'])
def get_power_by_id(id):
    power = Power.query.get(id)
    if power is None:
        return jsonify({"error": "Power not found"}), 404
    
    serialized_power = {
        "id": power.id,
        "name": power.name,
        "description": power.description
    }
    
    return jsonify(serialized_power)


@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.get(id)
    if power is None:
        return jsonify({"error": "Power not found"}), 404
    
    data = request.json
    if 'description' not in data:
        return jsonify({"errors": ["description is required"]}), 400
    power.description = data['description']
    errors = validate_power(power)
    if errors:
        return jsonify({"errors": errors}), 400
    db.session.commit()
    serialized_power = {
        "id": power.id,
        "name": power.name,
        "description": power.description
    }
    return jsonify(serialized_power)

def validate_power(power):
    errors = []
    if not power.description or len(power.description) < 20:
        errors.append("Description must be present and at least 20 characters long.")
    return errors


@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.json
    errors = validate_hero_power_data(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    hero_id = data.get('hero_id')
    power_id = data.get('power_id')
    strength = data.get('strength')
    
    hero = Hero.query.get(hero_id)
    if hero is None:
        return jsonify({"error": "Hero not found"}), 404
    
    power = Power.query.get(power_id)
    if power is None:
        return jsonify({"error": "Power not found"}), 404
    if strength not in ["Strong", "Weak", "Average"]:
        return jsonify({"error": "Strength must be one of: 'Strong', 'Weak', 'Average'"}), 400
    hero_power = HeroPower(hero_id=hero_id, power_id=power_id, strength=strength)
    db.session.add(hero_power)
    db.session.commit()
    serialized_hero_power = {
        "id": hero_power.id,
        "hero_id": hero_power.hero_id,
        "power_id": hero_power.power_id,
        "strength": hero_power.strength,
        "hero": {
            "id": hero.id,
            "name": hero.name,
            "super_name": hero.super_name
        },
        "power": {
            "id": power.id,
            "name": power.name,
            "description": power.description
        }
    }
    
    return jsonify(serialized_hero_power), 201

def validate_hero_power_data(data):
    errors = []
    if 'hero_id' not in data:
        errors.append("hero_id is required")
    if 'power_id' not in data:
        errors.append("power_id is required")
    if 'strength' not in data:
        errors.append("strength is required")
    return errors







if __name__ == '__main__':
    app.run(port=5555, debug=True)
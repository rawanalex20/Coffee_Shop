import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# ROUTES

# returns status code 200 and json {"success": True, "drinks": drinks}
# where drinks is the list of drinks
# or appropriate status code indicating reason for failure
try:
    @app.route('/drinks')
    def drinks():
        drinks = Drink.query.all()
        print(drinks[0].short())
        try:
            return jsonify({
                'success': True,
                'drinks': [drink.short() for drink in drinks]
            }), 200
        except:
            abort(422)
except:
    abort(401)

# returns status code 200 and json {"success": True, "drinks": drinks}
# where drinks is the list of drinks
# or appropriate status code indicating reason for failure
try:
    @app.route('/drinks-detail')
    @requires_auth('get:drinks-details')
    def drink_details(payload):
        try:
            print(payload)
            drinks = Drink.query.all()
            return jsonify({
                'success': True,
                'drinks': [drink.long() for drink in drinks]
            }), 200
        except:
            abort(422)
except:
    abort(401)

# returns status code 200 and json {"success": True, "drinks": drink}
# where drink an array containing only the newly created drink
# or appropriate status code indicating reason for failure
try:
    @app.route('/drinks', methods=['POST'])
    @requires_auth('post:drinks')
    def add_drink(payload):
        try:
            print(payload)
            body = request.get_json()
            title = body['title']
            recipes = body['recipe']
             if(type(recipes) == list):
                if len(recipes) == 0:
                    string_body = "[]"
                else:
                    string_body = "[{" + f"\"name\": \"{recipes[0]['name']}\", \"color\": \"{recipes[0]['color']}\", \"parts\": {recipes[0]['parts']}" + "}"
                    for recipe in recipes[1:len(recipes)]:
                        string_body = string_body + ",{" + f"\"name\": \"{recipe['name']}\", \"color\": \"{recipe['color']}\", \"parts\": {recipe['parts']}" + "}"
                    string_body = string_body + "]"
                print(string_body)
            else:
                string_body = "[{" + f"\"name\": \"{recipes['name']}\", \"color\": \"{recipes['color']}\", \"parts\": {recipes['parts']}" + "}]"
                print(string_body)
        
            drink = Drink(
                title=body['title'],
                recipe=string_body
                )
            db.session.add(drink)
            db.session.commit()
            print(drink.long())
            return jsonify({
                'success': True,
                'drinks': drink.long()
            }), 200
        except:
            abort(422)
except:
    abort(401)

# returns status code 200 and json {"success": True, "drinks": drink}
# where drink an array containing only the updated drink
# or appropriate status code indicating reason for failure
try:
    @app.route('/drinks/<id>', methods=['PATCH'])
    @requires_auth('patch:drinks')
    def patch_drink(payload, id):
        try:
            print(payload)
            drink = Drink.query.filter_by(id=id).all()[0]
            print(drink)
            body = request.get_json()
            string_body = str(body)
            if 'title' in string_body:
                title = body['title']
                drink.title=body['title']
            if 'recipe' in string_body:
                recipes = body['recipe']
                if(type(recipes) == list):
                    if len(recipes) == 0:
                        string_body = "[]"
                    else:
                        string_body = "[{" + f"\"name\": \"{recipes[0]['name']}\", \"color\": \"{recipes[0]['color']}\", \"parts\": {recipes[0]['parts']}" + "}"
                        for recipe in recipes[1:len(recipes)]:
                            string_body = string_body + ",{" + f"\"name\": \"{recipe['name']}\", \"color\": \"{recipe['color']}\", \"parts\": {recipe['parts']}" + "}"
                        string_body = string_body + "]"
                    print(string_body)
                else:
                    string_body = "[{" + f"\"name\": \"{recipes['name']}\", \"color\": \"{recipes['color']}\", \"parts\": {recipes['parts']}" + "}]"
                    print(string_body)
                drink.recipe=string_body
            db.session.commit()
            print(drink.long())
            return jsonify({
                'success': True,
                'drinks': [drink.long()]
            }), 200
        except:
            abort(422)
except:
    abort(401)

# returns status code 200 and json {"success": True, "delete": id}
# where id is the id of the deleted record
# or appropriate status code indicating reason for failure
try:
    @app.route('/drinks/<id>', methods=['DELETE'])
    @requires_auth('delete:drinks')
    def delete_drink(payload, id):
        try:
            print(payload)
            drink = Drink.query.filter_by(id=id).all()[0]
            print(drink)
            drink.delete()
            db.session.commit()
            return jsonify({
                "success": True,
                 "delete": id
            }), 200
        except:
            abort(422)
except:
    abort(401)

# error handler for 422
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


# error handler for 404
@app.errorhandler(404)
def bad_request(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

# error handler for 401
@app.errorhandler(401)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
        }), 401

# error handler for 405
@app.errorhandler(405)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
        }), 405

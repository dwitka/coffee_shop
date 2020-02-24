import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
# CORS(app)

CORS(app, resources={r"/api/*": {"origins": "*"}})


# Use the after_request decorator to set Access-Control-Allow
@app.after_request
def after_request(response):
    response.headers.add(
        'Access-Control-Allow-Origin', 'http://localhost:8100')
    response.headers.add(
        'Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add(
        'Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response


db_drop_and_create_all()

'''
uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
'''
implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where
    drinks is the list of drinks or appropriate status code indicating reason
    for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    '''returns a list of drinks'''
    drinks = Drink.query.all()
    drinks_list = []
    count = 0
    if len(drinks) != 0:
        while count < len(drinks):
            drinks_list.append(drinks[count].short())
            count = count + 1
    else:
        pass
    return jsonify({"success": True, "drinks": drinks_list}), 200


'''
implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where
    drinks is the list of drinks or appropriate status code indicating reason
    for failure
'''
@app.route('/drinks-detail', methods=['GET'])
def get_drinks_detail():
    '''returns a list of drinks in drink.long() format'''
    if 'Authorization' not in request.headers:
        abort(401)
    if not requires_auth(permission='get:drinks-detail'):
        raise AuthError({
            'code': 'invalid_permission',
            'description': 'Do not have permission to view drinks-detail.'
        }, 403)
    drinks = []
    data = Drink.query.all()
    for drink in data:
        drinks.append(drink.long())
    return jsonify({"success": True,
                    "drinks": drinks}), 200


'''
implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where
    drink is an array containing only the newly created drink or appropriate
    status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
def add_drinks():
    '''creates a new row in the drinks table'''
    if not requires_auth(permission='post:drinks'):
        raise AuthError({
            'code': 'invalid_permission',
            'description': 'Do not have permission to make drinks.'
        }, 403)
    else:
        data = request.get_json()
    if data:
        new_recipe = data['recipe']
        drink = Drink(title=data['title'], recipe=json.dumps(new_recipe))
        drink.insert()
    else:
        abort(401)
    return jsonify({"success": True,
                    "drinks": [drink.long()]}), 200


'''
implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where
    drink an array containing only the updated drink or appropriate status code
    indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
def edit_title(id):
    '''changes the name of the drink'''
    if not requires_auth(permission='patch:drinks'):
        raise AuthError({
            'code': 'invalid_permission',
            'description': 'Do not have permission to edit.'
        }, 403)
    drink = Drink.query.filter_by(id=id).one_or_none()
    if not drink:
        abort(401)
    else:
        try:
            data = request.get_json()
            new_title = data['title']
            drink.title = new_title
            drink.update()
        except Exception:
            abort(422)
    return jsonify({"success": True, "drinks": [drink.long()]}), 200


'''
implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id
    is the id of the deleted record or appropriate status code indicating
    reason for failure
'''
@app.route('/drinks/<id>', methods=['DELETE'])
def delete_drink(id):
    '''deletes a drink'''
    if not requires_auth(permission='delete:drinks'):
        raise AuthError({
            'code': 'invalid_permission',
            'description': 'permission to delete not granted.'
        }, 403)
    drink = Drink.query.filter_by(id=id).one_or_none()
    if not drink:
        abort(401)
    else:
        drink.delete()
        return jsonify({"success": True, "delete": id}), 200


# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


'''
implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404
'''
@app.errorhandler(403)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 403,
                    "message": "don't have permissions"
                    }), 403


'''
implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404


@app.errorhandler(401)
def resource_not_found(error):
    return jsonify({
                    "success": False,
                    "error": 401,
                    "message": "Unauthorized"
                    }), 401


'''
implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def autherror(error):
    return jsonify({
                    "success": False,
                    "error": AuthError,
                    "message": "AuthError"
                    }), AuthError

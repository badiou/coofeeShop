import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)
db_drop_and_create_all()

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
## ROUTES


############################################################################################################
#
#                                          GET/drinks
#
###########################################################################################################

@app.route('/drinks')
@requires_auth('get:drinks')
def get_all_drinks():
    drinks=Drink.query.order_by(id).all()
    formatted_drinks=[drink.short() for drink in drinks]
    return jsonify({
        'sucess':True,
        'drinks': formatted_drinks
    })


############################################################################################################
#
#                                          GET/drinks-detail
#
###########################################################################################################

@app.route('/drinks-details')
@requires_auth('get:drinks-detail')
def drinks_details():
    drinks=Drink.query.order_by(id).all()
    formatted_drinks=[drink.long() for drink in drinks]
    return jsonify({
        'sucess':True,
        'drinks': formatted_drinks
    })


############################################################################################################
#
#                                           POST /drinks
#
###########################################################################################################

@app.route('/drinks',methods=['POST'])
@requires_auth('post:drinks')
def create_drink():
    body=request.get_json()
    new_title=body.get('title',None)
    new_recipe=body.get('recipe',None) 
    try: 
        drink=Drink(title=new_title, recipe=new_recipe)
        drink.insert()
        drinks=Drink.query.order_by(id).all()
        formatted_long_drinks=[ drink.long() for drink in drinks]
        return jsonify({
          'success':True,
          'drinks':formatted_long_drinks,      
        })
    except:
      abort(422)


############################################################################################################
#
#                                       PATCH /drinks/<id>
#
###########################################################################################################
@app.route('/drinks/<int:drink_id>',methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(drink_id):
    body=request.get_json()
    try:
      drink_updated=Drink.query.filter(Drink.id==drink_id).one_or_none()
      if drink is None:
            abort(404)
      if 'recipe' in body and 'title' in body:
        drink.title=body.get('title',None)
        drink.recipe=body.get('recipe',None)   
      drink.update()
      formatted_updated_drink=[ drink_updated.long()]
      return jsonify({
        'success':True,
        'drinks':formatted_updated_drink
      })
    except:
      abort(400) # Bad request. The user send request that server could not be understand

############################################################################################################
#
#                                         DELETE /drinks/<id>
#
###########################################################################################################

@app.route('/drinks/<int:drink_id>',methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(drinks_id):
    try:
      drink=Drink.query.filter(Drink.id==drink_id).one_or_none()
      if drink is None:
        abort(404,{'Drink does not exist. Please, provide a another id'})
      drink.delete()
      return jsonify({
        'success':True,
        'deleted':drink_id
      })
    except:
      abort(422) #Unprocessable Entity

############################################################################################################
#
#                                         Error Handling
#
###########################################################################################################

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({'success': False, 'error': 422,
            'message': 'Unproccessable'}), 422
@app.errorhandler(404)
def not_found(error):
    return (jsonify({'success': False, 'error': 404,
            'message': 'Not found'}), 404

@app.errorhandler(400)
def error_client(error):
    return (jsonify({'success': False, 'error': 400,
            'message': 'Bad request'}), 400

@app.errorhandler(500)
def server_error(error):
    return (jsonify({'success': False, 'error': 500,
            'message': 'internal server error'}), 500)

@app.errorAuth(AuthError)
def get_error_from_authenfication(AuthError):
    return (jsonify({'success': False, 'error': 401,
            'message': AuthError.error}), 401

			
			
			
			
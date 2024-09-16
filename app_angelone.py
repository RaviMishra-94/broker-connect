"""
AngelOne API Flask Application - Operational Overview

This Flask application serves as a RESTful API interface for the AngelOne trading platform. Here's how it operates:

1. Initialization:
   - The Flask app is created and configured with CORS support.
   - Various route handlers are defined for different API endpoints.

2. Authentication Flow:
   - Users initiate a session via '/generate-session', providing API key, client code, password, and TOTP.
   - The app uses these credentials to authenticate with AngelOne and returns a JWT token.
   - This token is used in subsequent requests for authorization.
   - Token renewal and session termination are handled by separate endpoints.

3. Trading Operations:
   - Authenticated users can place, modify, or cancel orders through respective endpoints.
   - Each trading operation initializes an AngelOne instance with the user's API key and JWT token.
   - The app translates incoming JSON data into AngelOne SDK objects (e.g., Order) for processing.
   - Responses from AngelOne are converted back to JSON for the client.

4. Error Handling and Logging:
   - Each endpoint is wrapped in a try-except block to catch and report errors.
   - Errors are logged and returned to the client in a consistent JSON format.
   - Successful operations are also logged for tracking and debugging purposes.


The application acts as a bridge between client applications and the AngelOne trading platform, 
handling authentication, translating requests, processing trades, and managing data flow. It 
provides a unified interface for various trading and portfolio management operations while 
abstracting the complexities of direct interaction with the AngelOne SDK.
"""

from flask import Flask, jsonify, render_template
from common.decorators_routes import extract_keys
from angelone.angelone import AngelOne, Order
from flask_cors import CORS
import pyotp
import json
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/generate-session', methods=['POST'])
@extract_keys('apiKey', 'clientCode', 'password', 'qrValue')
def login(request_data):
    try:
        totp = pyotp.TOTP(request_data['qrValue']).now()
        angel_instance = AngelOne(api_key=request_data['apiKey'])
        result = angel_instance.generateSession(request_data['clientCode'], request_data['password'], totp)
        return jsonify(result)
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

@app.route('/terminate-session', methods=['POST'])
@extract_keys('apiKey', 'jwtToken', 'clientCode')
def logout(request_data):
    try:
        angel_instance = AngelOne(api_key=request_data['apiKey'], access_token=request_data['jwtToken'])
        result = angel_instance.terminateSession(request_data['clientCode'])
        return jsonify(result)
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

@app.route('/generate-token', methods=['POST'])
@extract_keys('apiKey', 'jwtToken', 'refreshToken')
def generate_token(request_data):
    try:
        angel_instance = AngelOne(api_key=request_data['apiKey'], access_token=request_data['jwtToken'])
        result = angel_instance.generateToken(request_data['refreshToken'])
        return jsonify(result)
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500
   
@app.route('/renew-token', methods=['POST'])
@extract_keys('apiKey', 'jwtToken')
def renew_token(request_data):
    try:
        angel_instance = AngelOne(api_key=request_data['apiKey'], access_token=request_data['jwtToken'])
        result = angel_instance.renewAccessToken()
        return jsonify(result)
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500
    
@app.route('/profile', methods=['POST'])
@extract_keys('apiKey', 'jwtToken', 'refreshToken')
def get_profile(request_data):
    try:
        angel_instance = AngelOne(api_key=request_data['apiKey'], access_token=request_data['jwtToken'])
        result = angel_instance.getProfile(request_data['refreshToken'])
        return jsonify(result)
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

@app.route('/place-order', methods=['POST'])
@extract_keys('apiKey', 'jwtToken', 'order')
def place_order(request_data):
    try:
        angel_instance = AngelOne(api_key=request_data['apiKey'], access_token=request_data['jwtToken'])
        order = Order(**request_data['order'])
        result = angel_instance.placeOrder(order)
        return jsonify(result.to_dict())
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

@app.route('/modify-order', methods=['POST'])
@extract_keys('apiKey', 'jwtToken', 'order', 'orderId') # check which order id is required
def modify_order(request_data):
    try:
        angel_instance = AngelOne(api_key=request_data['apiKey'], access_token=request_data['jwtToken'])
        order = Order(**request_data['order'])
        result = angel_instance.modifyOrder(order, request_data['orderId'])
        return jsonify(result.to_dict())
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

@app.route('/cancel-order', methods=['POST'])
@extract_keys('apiKey', 'jwtToken', 'variety', 'orderId') # check which order id is required
def cancel_order(request_data):
    try:  
        angel_instance = AngelOne(api_key=request_data['apiKey'], access_token=request_data['jwtToken'])
        result = angel_instance.cancelOrder(request_data['variety'], request_data['orderId'])
        return jsonify(result.to_dict())
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

@app.route('/order-book', methods=['POST'])
@extract_keys('apiKey', 'jwtToken')
def get_order_book(request_data):
    try:
        angel_instance = AngelOne(api_key=request_data['apiKey'], access_token=request_data['jwtToken'])
        result = angel_instance.getOrderBook()
        return jsonify(result.to_dict())
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

@app.route('/trade-book', methods=['POST'])
@extract_keys('apiKey', 'jwtToken')
def get_trade_book(request_data):
    try:
        angel_instance = AngelOne(api_key=request_data['apiKey'], access_token=request_data['jwtToken'])
        result = angel_instance.getTradeBook()
        return jsonify(result.to_dict())
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500
   
@app.route('/single-order-status', methods=['POST'])
@extract_keys('apiKey', 'jwtToken', 'uniqueorderid')
def get_single_order_status(request_data):
        try:
            angel_instance = AngelOne(api_key=request_data['apiKey'], access_token=request_data['jwtToken'])
            order_response = angel_instance.getOrderStatus(request_data['uniqueorderid'])
            return jsonify(order_response.to_dict())
        except Exception as error:
            return jsonify({"error@route": str(error), "status": 1}), 500
        
@app.route('/order-statuses', methods=['POST'])
@extract_keys('apiKey', 'jwtToken', 'uniqueorderids')
def get_mutiple_order_status(request_data):
    try:
        angel_instance = AngelOne(api_key=request_data['apiKey'], access_token=request_data['jwtToken'])
        uniqueorderids = request_data['uniqueorderids']
        if not isinstance(uniqueorderids, list):
            return jsonify({"error": "uniqueorderids should be a list", "status": 1}), 400

        results = []
        for uniqueorderid in uniqueorderids:
            order_response = angel_instance.getOrderStatus(uniqueorderid)
            order_response = order_response.to_dict()

            if order_response is None:
                results[uniqueorderid] = {
                    "errorcode": order_response.get("errorcode", ""),
                    "message": order_response.get("message", "Order details not found."),
                    "status": order_response.get("status", False)
                }
                continue
            results.append(order_response)
        return jsonify(results)
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500
        
@app.route('/holdings', methods=['POST'])
@extract_keys('apiKey', 'jwtToken')
def get_holdings(request_data):
    try:
        angel_instance = AngelOne(api_key=request_data['apiKey'], access_token=request_data['jwtToken'])
        result = angel_instance.getHolding()
        return jsonify(result.to_dict())
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

@app.route('/all-holdings', methods=['POST'])
@extract_keys('apiKey', 'jwtToken')
def get_all_holdings(request_data):
    try:
        angel_instance = AngelOne(api_key=request_data['apiKey'], access_token=request_data['jwtToken'])
        result = angel_instance.getAllHolding()
        return jsonify(result)
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500
    
@app.route('/positions', methods=['POST'])
@extract_keys('apiKey', 'jwtToken')
def get_positions(request_data):
    try:
        angel_instance = AngelOne(api_key=request_data['apiKey'], access_token=request_data['jwtToken'])
        result = angel_instance.getPosition()
        return jsonify(result.to_dict())
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

@app.route('/funds', methods=['POST'])
@extract_keys('apiKey', 'jwtToken')
def get_funds(request_data):
    try:
        angel_instance = AngelOne(api_key=request_data['apiKey'], access_token=request_data['jwtToken'])
        result = angel_instance.getFunds()
        return jsonify(result)
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

if __name__ == '__main__':
    app.run(debug=True)

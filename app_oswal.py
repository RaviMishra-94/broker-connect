"""
Oswal API Flask Application - Operational Overview

This Flask application serves as a RESTful API interface for the Oswal trading platform. Here's how it operates:

1. Initialization:
   - The Flask app is created and configured with CORS support.
   - Various route handlers are defined for different API endpoints.

2. Authentication Flow:
   - Users initiate a session via '/generate-session', providing API key, client code, password, and TOTP.
   - The app uses these credentials to authenticate with Oswal and returns a JWT token.
   - This token is used in subsequent requests for authorization.
   - Token renewal and session termination are handled by separate endpoints.

3. Trading Operations:
   - Authenticated users can place, modify, or cancel orders through respective endpoints.
   - Each trading operation initializes an Oswal instance with the user's API key and JWT token.
   - The app translates incoming JSON data into Oswal SDK objects (e.g., Order) for processing.
   - Responses from Oswal are converted back to JSON for the client.

4. Error Handling and Logging:
   - Each endpoint is wrapped in a try-except block to catch and report errors.
   - Errors are logged and returned to the client in a consistent JSON format.
   - Successful operations are also logged for tracking and debugging purposes.


The application acts as a bridge between client applications and the Oswal trading platform, 
handling authentication, translating requests, processing trades, and managing data flow. It 
provides a unified interface for various trading and portfolio management operations while 
abstracting the complexities of direct interaction with the Oswal SDK.
"""

from flask import Flask, jsonify, render_template
from common.decorators_routes import extract_keys
from Oswal import Oswal, Order
from flask_cors import CORS
import json
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/generate-session', methods=['POST'])
@extract_keys('apiKey', 'clientCode', 'password', 'totp','two_fa')
def login(request_data):
    try:
        oswal_instance = Oswal(api_key=request_data['apiKey'],client_code=request_data['clientId'])
        result = oswal_instance.login(request_data['password'],request_data['two_fa'],request_data['totp'])
        return jsonify(result)
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

@app.route('/terminate-session', methods=['POST'])
@extract_keys('apiKey', 'jwtToken', 'clientCode')
def logout(request_data):
    try:
        oswal_instance = Oswal(api_key=request_data['apiKey'], client_code=request_data['clientCode'])
        result = oswal_instance.logout()
        return jsonify(result)
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

    
@app.route('/profile', methods=['POST'])
@extract_keys('apiKey', 'clientCode')
def get_profile(request_data):
    try:
        oswal_instance = Oswal(api_key=request_data['apiKey'], client_code=request_data['clientCode'])
        result = oswal_instance.GetProfile()
        return jsonify(result)
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

@app.route('/place-order', methods=['POST'])
@extract_keys('apiKey', 'clientCode','place_order_info')
def place_order(request_data):
    try:
        oswal_instance = Oswal(api_key=request_data['apiKey'], client_code=request_data['clientCode'])
        result = oswal_instance.PlaceOrder(request_data['place_order_info'])
        return jsonify(result.to_dict())
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

@app.route('/modify-order', methods=['POST'])
@extract_keys('apiKey', 'clientCode','modify_order_info')
def modify_order(request_data):
    try:
        oswal_instance = Oswal(api_key=request_data['apiKey'], client_code=request_data['clientCode'])
        result = oswal_instance.ModifyOrder(request_data['modify_order_info'])
        return jsonify(result.to_dict())
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

@app.route('/cancel-order', methods=['POST'])
@extract_keys('apiKey', 'clientCode','orderId') # check which order id is required
def cancel_order(request_data):
    try:  
        oswal_instance = Oswal(api_key=request_data['apiKey'], client_code=request_data['clientCode'])
        result = oswal_instance.CancelOrder(request_data['orderId'])
        return jsonify(result.to_dict())
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

@app.route('/order-book', methods=['POST'])
@extract_keys('apiKey', 'clientCode')
def get_order_book(request_data):
    try:
        oswal_instance = Oswal(api_key=request_data['apiKey'], client_code=request_data['clientCode'])
        result = oswal_instance.GetOrderBook()
        return jsonify(result.to_dict())
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

@app.route('/trade-book', methods=['POST'])
@extract_keys('apiKey', 'clientCode')
def get_trade_book(request_data):
    try:
        oswal_instance = Oswal(api_key=request_data['apiKey'], client_code=request_data['clientCode'])
        result = oswal_instance.GetTradeBook(request_data['clientCode'])
        return jsonify(result.to_dict())
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500
   

        
@app.route('/holdings', methods=['POST'])
@extract_keys('apiKey', 'clientCode')
def get_holdings(request_data):
    try:
        oswal_instance = Oswal(api_key=request_data['apiKey'], client_code=request_data['clientCode'])
        result = oswal_instance.GetHoldings()
        return jsonify(result.to_dict())
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500


@app.route('/positions', methods=['POST'])
@extract_keys('apiKey', 'clientCode')
def get_positions(request_data):
    try:
        oswal_instance = Oswal(api_key=request_data['apiKey'], client_code=request_data['clientCode'])
        result = oswal_instance.GetPosition()
        return jsonify(result.to_dict())
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500



if __name__ == '__main__':
    app.run(debug=True)

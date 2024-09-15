from flask import Flask, jsonify, render_template
from common.decorators_routes import extract_keys
from dhan.dhan import Dhan, Order
from flask_cors import CORS
import pyotp
import json
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/place-order', methods=['POST'])
@extract_keys('clientId', 'accessToken', 'order')
def place_order(request_data):
    try:
        dhan_instance = Dhan(client_id=request_data['clientId'], access_token=request_data['accessToken'])
        order = Order(**request_data['order'])
        result = dhan_instance.placeOrder(order)
        return jsonify(result.to_dict())
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

@app.route('/modify-order', methods=['POST'])
@extract_keys('clientId', 'accessToken', 'order', 'orderId') # check which order id is required
def modify_order(request_data):
    try:
        dhan_instance = Dhan(client_id=request_data['clientId'], access_token=request_data['accessToken'])
        order = Order(**request_data['order'])
        result = dhan_instance.modifyOrder(order, request_data['orderId'])
        return jsonify(result.to_dict())
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

@app.route('/cancel-order', methods=['POST'])
@extract_keys('clientId', 'accessToken', 'orderId') # check which order id is required
def cancel_order(request_data):
    try:  
        dhan_instance = Dhan(client_id=request_data['clientId'], access_token=request_data['accessToken'])
        result = dhan_instance.cancelOrder(request_data['orderId'])
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
@extract_keys('clientId', 'accessToken')
def get_trade_book(request_data):
    try:
        dhan_instance = Dhan(client_id=request_data['clientId'], access_token=request_data['accessToken'])
        result = dhan_instance.getTradeBook()
        return jsonify(result.to_dict())
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500
   
@app.route('/single-order-status', methods=['POST'])
@extract_keys('clientId', 'accessToken', 'orderid')
def get_single_order_status(request_data):
        try:
            dhan_instance = Dhan(client_id=request_data['clientId'], access_token=request_data['accessToken'])
            order_response = dhan_instance.getOrderStatus(request_data['orderId'])
            return jsonify(order_response.to_dict())
        except Exception as error:
            return jsonify({"error@route": str(error), "status": 1}), 500
        
@app.route('/order-statuses', methods=['POST'])
@extract_keys('clientId', 'accessToken', 'orderids')
def get_mutiple_order_status(request_data):
    try:
        dhan_instance = Dhan(client_id=request_data['clientId'], access_token=request_data['accessToken'])
        orderids = request_data['orderids']
        if not isinstance(uniqueorderids, list):
            return jsonify({"error": "orderids should be a list", "status": 1}), 400

        results = []
        for orderid in orderids:
            order_response = angel_instance.getOrderStatus(orderid)
            order_response = order_response.to_dict()

            if order_response is None:
                results[orderid] = {
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
@extract_keys('clientId', 'accessToken')
def get_holdings(request_data):
    try:
        dhan_instance = Dhan(client_id=request_data['clientId'], access_token=request_data['accessToken'])
        result = dhan_instance.getHolding()
        return jsonify(result.to_dict())
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500
    
@app.route('/positions', methods=['POST'])
@extract_keys('clientId', 'accessToken')
def get_positions(request_data):
    try:
        dhan_instance = Dhan(client_id=request_data['clientId'], access_token=request_data['accessToken'])
        result = dhan_instance.getPosition()
        return jsonify(result.to_dict())
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

@app.route('/funds', methods=['POST'])
@extract_keys('clientId', 'accessToken')
def get_funds(request_data):
    try:
        dhan_instance = Dhan(client_id=request_data['clientId'], access_token=request_data['accessToken'])
        result = dhan_instance.getFunds()
        return jsonify(result)
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

if __name__ == '__main__':
    app.run(debug=True)

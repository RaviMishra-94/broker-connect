from flask import Flask, jsonify, render_template
from common.decorators_routes import extract_keys
from dhan.dhan import Dhan, Order
from flask_cors import CORS
import pyotp
import json
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def generate_consent_login_url(consentId):
    dhan_instance = Dhan()
    return dhan_instance.generateConsentLoginUrl(consentId)

@app.route('/dhan/generate-consent', methods=['POST'])
@extract_keys('partner_id', 'partner_secret')
def generate_consent(request_data):
    try:
        dhan_instance = Dhan(partner_id=request_data['partner_id'], partner_secret=request_data['partner_secret'])
        consentId = dhan_instance.generateConsent()
        return jsonify({"consentId": consentId})
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

@app.route('/dhan/consume-consent', methods=['POST'])
@extract_keys('partner_id', 'partner_secret')
def consume_consent(request_data):
    try:
        dhan_instance = Dhan(partner_id=request_data['partner_id'], partner_secret=request_data['partner_secret'])
        userDetails = dhan_instance.consumeConsent(request_data['token-Id'])
        return jsonify({"dhanClientId": userDetails["dhanClientId"], "accessToken": userDetails["accessToken"]})
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

@app.route('/dhan/place-order', methods=['POST'])
@extract_keys('clientId', 'accessToken', 'order')
def place_order(request_data):
    try:
        dhan_instance = Dhan(client_id=request_data['clientId'], access_token=request_data['accessToken'])
        order = Order(**request_data['order'])
        result = dhan_instance.placeOrder(order)
        return jsonify(result.to_dict())
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

@app.route('/dhan/modify-order', methods=['POST'])
@extract_keys('clientId', 'accessToken', 'order', 'orderId') # check which order id is required
def modify_order(request_data):
    try:
        dhan_instance = Dhan(client_id=request_data['clientId'], access_token=request_data['accessToken'])
        order = Order(**request_data['order'])
        result = dhan_instance.modifyOrder(order, request_data['orderId'])
        return jsonify(result.to_dict())
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

@app.route('/dhan/cancel-order', methods=['POST'])
@extract_keys('clientId', 'accessToken', 'orderId') # check which order id is required
def cancel_order(request_data):
    try:  
        dhan_instance = Dhan(client_id=request_data['clientId'], access_token=request_data['accessToken'])
        result = dhan_instance.cancelOrder(request_data['orderId'])
        return jsonify(result.to_dict())
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

@app.route('/dhan/order-book', methods=['POST'])
@extract_keys('clientId', 'accessToken')
def get_order_book(request_data):
    try:
        dhan_instance = Dhan(client_id=request_data['clientId'], access_token=request_data['accessToken'])
        result = dhan_instance.getOrderBook()
        return jsonify(result.to_dict())
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

@app.route('/dhan/trade-book', methods=['POST'])
@extract_keys('clientId', 'accessToken')
def get_trade_book(request_data):
    try:
        dhan_instance = Dhan(client_id=request_data['clientId'], access_token=request_data['accessToken'])
        result = dhan_instance.getTradeBook()
        return jsonify(result.to_dict())
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500
   
@app.route('/dhan/single-order-status', methods=['POST'])
@extract_keys('clientId', 'accessToken', 'uniqueOrderId')
def get_single_order_status(request_data):
    try:
        dhan_instance = Dhan(client_id=request_data['clientId'], access_token=request_data['accessToken'])
        order_response = dhan_instance.getOrderStatus(request_data['uniqueOrderId'])
        return jsonify(order_response.to_dict())
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500
        
@app.route('/dhan/order-statuses', methods=['POST'])
@extract_keys('clientId', 'accessToken', 'uniqueOrderIds')
def get_mutiple_order_status(request_data):
    try:
        dhan_instance = Dhan(client_id=request_data['clientId'], access_token=request_data['accessToken'])
        orderids = request_data['uniqueOrderIds']
        if not isinstance(orderids, list):
            return jsonify({"error": "orderids should be a list", "status": 1}), 400

        results = []
        for orderid in orderids:
            order_response = dhan_instance.getOrderStatus(orderid)
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
        
@app.route('/dhan/holdings', methods=['POST'])
@extract_keys('clientId', 'accessToken')
def get_holdings(request_data):
    try:
        dhan_instance = Dhan(client_id=request_data['clientId'], access_token=request_data['accessToken'])
        result = dhan_instance.getHolding()
        return jsonify(result.to_dict())
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500
    
@app.route('/dhan/positions', methods=['POST'])
@extract_keys('clientId', 'accessToken')
def get_positions(request_data):
    try:
        dhan_instance = Dhan(client_id=request_data['clientId'], access_token=request_data['accessToken'])
        result = dhan_instance.getPosition()
        result = result.to_dict()
        return jsonify(result)
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

@app.route('/dhan/funds', methods=['POST'])
@extract_keys('clientId', 'accessToken')
def get_funds(request_data):
    try:
        dhan_instance = Dhan(client_id=request_data['clientId'], access_token=request_data['accessToken'])
        result = dhan_instance.getFunds()
        return jsonify(result)
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500


@app.route('/dhan/tpin', methods=['POST'])
@extract_keys('clientId', 'accessToken')
def generate_tpin(request_data):
    try:
        dhan_instance = Dhan(access_token=request_data['accessToken'])
        result = dhan_instance.generateTpin()
        print(result)
        return jsonify(result)
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500


@app.route('/dhan/verify/tpin', methods=['POST'])
@extract_keys('clientId', 'accessToken', 'isin')
def verify_tpin(request_data):
    try:
        dhan_instance = Dhan(access_token=request_data['accessToken'])
        isin = request_data.get('isin', "")
        result = dhan_instance.enter_tpin(isin)
        print(result)
        return jsonify({"edisFormHtml": result})
    except Exception as error:
        return jsonify({"error@route": str(error), "status": 1}), 500

if __name__ == '__main__':
    app.run(debug=True)

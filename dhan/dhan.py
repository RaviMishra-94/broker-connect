import ssl
from urllib.parse import urljoin
import requests as req
from typing import Union
import socket
import uuid
import re
import logging
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from .dhan_scrip import getSecurityIdFromTradingSymbol
from logzero import  logger
# Import other necessary modules for response and order handling
from body.Order import Order
from body.Response import OrderResponse, OrderBookStructure, OrderBookResponse, TradeBookStructure, TradeBookResponse, \
    OrderStatusResponse, HoldingResponseStructure, HoldingResponse, PositionResponseStructure, PositionResponse, \
    ErrorResponse
from decorators import handle_parse_error
from datetime import datetime, timezone

log = logging.getLogger(__name__)

class Dhan(object):
    _rootUrl = "https://api.dhan.co"
    _authUrl = "https://auth.dhan.co"
    _default_timeout = 7  # seconds

    _routes = {

        #Authentication
        "api.generate.consent": "/partner/generate-consent",
        "api.consent.login": "/consent-login",
        "api.consume.consent": "/consume-consent",

        # Order Management
        "api.order.place": "/v2/orders",  # Place a new order
        "api.order.modify": "/v2/orders/{order-id}",  # Modify existing order
        "api.order.cancel": "/v2/orders/{order-id}",  # Cancel order
        "api.order.book": "/v2/orders",  # Retrieve all orders of the day

        # Trade Book and Positions
        "api.trade.book": "/v2/trades",  # Fetch trade book
        "api.holding": "/holdings",  # Get holdings
        "api.position": "/v2/positions",  # Get positions
        "api.funds": "/v2/fundlimit",  # Get fund details
        "api.order.status": "v2/orders/{order-id}", #Get order details/status

        #EDIS
        "api.generate.tpin": "edis/tpin",
        "api.enter.tpin": "edis/form"

    }

    # Fetching local and public IP addresses and MAC address of the device
    try:
        clientPublicIp = req.get('https://api.ipify.org').text.strip()
        hostname = socket.gethostname()
        clientLocalIp = socket.gethostbyname(hostname)
    except Exception as e:
        print(e)
        clientPublicIp, clientLocalIp = "106.193.147.98", "127.0.0.1"
    
    clientMacAddress = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
    accept = "application/json"
    userType = "USER"
    sourceID = "WEB"

    def __init__(self, partner_id=None, partner_secret=None, redirect_url=None, client_id=None, access_token=None, session_expiry_hook=None, debug=False, disable_ssl=False, timeout=7, proxies=None):
        self.access_token = access_token
        self.session_expiry_hook = session_expiry_hook
        self.debug = debug
        self.disable_ssl = disable_ssl
        self.timeout = timeout
        self.proxies = proxies
        self.client_id = client_id
        self.partner_id = partner_id
        self.partner_secret = partner_secret
        self.redirect_url = redirect_url

    def setSessionExpiryHook(self, method):
        """Set a custom session expiry hook."""
        if not callable(method):
            raise ValueError("Invalid input type. Only functions are accepted")
        self.session_expiry_hook = method

    def requestAuthHeaders(self):
        headers = {}
        headers["partner_id"] = self.partner_id
        headers["partner_secret"] = self.partner_secret
        return headers

    def _authRequest(self, route, method, parameters=None):
        """Make an HTTP request"""
        params = parameters.copy() if parameters else {}

        # Build URL
        uri = self._routes[route].format(**params)
        url = urljoin(self._authUrl, uri)

        # Custom Headers
        headers = self.requestAuthHeaders()

        # print(f"Request: {method} {url} {params} {headers}")

        try:
            # Send request
            r = req.request(method,
                            url,
                            data=json.dumps(params) if method in ["POST", "PUT"] else None,
                            params=params if method in ["GET", "DELETE"] else None,
                            headers=headers,
                            verify=not self.disable_ssl,
                            allow_redirects=True,
                            timeout=self.timeout,
                            proxies=self.proxies)

        except Exception as e:
            log.error(f"Error occurred while making a {method} request to {url}. Headers: {headers}, Request: {params}, Response: {e}")
            raise e

        if self.debug:
            log.debug(f"Response: {r.status_code} {r.content}")

        if r.status_code == 401:
            log.error(f"Unauthorized access: {method} request to {url}. Headers: {headers}, Request: {params}, Response Code: {r.status_code}")
            
            # Return a custom message with the response data
            return {
                "status": 0,
                "message": "Unauthorized access - Authentication failed.",
                "data": {}
            }

        # Parse response
        try:
            data = json.loads(r.content.decode("utf8"))
        except ValueError:
            raise Exception(f"Couldn't parse the JSON response: {r}")
        return data

    def requestHeaders(self):
        headers = {"content-type": "application/json"}
        if self.access_token:
            headers["access-token"] = self.access_token
        return headers

    def _getAuthRequest(self, route, params=None):
        """Alias for sending a GET request."""
        return self._authRequest(route, "GET", params)
    
    def _request(self, route, method, parameters=None):
        """Make an HTTP request"""
        params = parameters.copy() if parameters else {}

        # Build URL
        uri = self._routes[route].format(**params)
        url = urljoin(self._rootUrl, uri)

        # Custom Headers
        headers = self.requestHeaders()

        if self.access_token:
            # Set authorization header
            headers["access-token"] = self.access_token

        if self.debug:
            log.debug(f"Request: {method} {url} {params} {headers}")

        print(f"Request: {method} {url} {params} {headers}")

        try:
            # Send request
            r = req.request(method,
                            url,
                            data=json.dumps(params) if method in ["POST", "PUT"] else None,
                            params=params if method in ["GET", "DELETE"] else None,
                            headers=headers,
                            verify=not self.disable_ssl,
                            allow_redirects=True,
                            timeout=self.timeout,
                            proxies=self.proxies)

        except Exception as e:
            log.error(f"Error occurred while making a {method} request to {url}. Headers: {headers}, Request: {params}, Response: {e}")
            raise e

        if self.debug:
            log.debug(f"Response: {r.status_code} {r.content}")

        # Parse response
        if r.headers.get("Content-Type") == "application/json":
            try:
                data = json.loads(r.content.decode("utf8"))
            except ValueError:
                raise Exception(f"Couldn't parse the JSON response: {r.content}")
            return data
        elif r.headers.get("Content-Type") == "text/csv":
            return r.content
        else:
            raise Exception(f"Unknown Content-Type ({r.headers.get('Content-Type')}) with response: ({r.content})")

    def _deleteRequest(self, route, params=None):
        """Alias for sending a DELETE request."""
        return self._request(route, "DELETE", params)

    def _putRequest(self, route, params=None):
        """Alias for sending a PUT request."""
        return self._request(route, "PUT", params)

    def _postRequest(self, route, params=None):
        """Alias for sending a POST request."""
        return self._request(route, "POST", params)

    def _getRequest(self, route, params=None):
        """Alias for sending a GET request."""
        return self._request(route, "GET", params)
    
    @staticmethod
    def _getTransactionType(order: Order) -> str:
        """Get transaction type for angel one
            :returns 'BUY' or 'SELL'"""
        transactionType = order.transactionType
        if re.match(r"^(BUY|SELL)$", transactionType, re.IGNORECASE):
            return transactionType.upper()
        else:
            logger.error(f"Invalid transaction type: {transactionType}")
            return ""

    @staticmethod
    def _getOrderType(order: Order) -> str:
        """Get order type for angel one
            :returns MARKET|LIMIT|STOPLOSS_LIMIT|STOPLOSS_MARKET"""
        orderType = order.orderType
        if re.match(r"^(MARKET|LIMIT|STOP_LOSS|STOPLOSS_MARKET)$", orderType, re.IGNORECASE):
            return orderType.upper()
        else:
            logger.error(f"Invalid order type: {orderType}")
            return "LIMIT"

    @staticmethod
    def _getProductType(order: Order) -> str:
        """Get product type for angel one
            :returns INTRADAY|DELIVERY|CARRYFORWARD|MARGIN|BO"""
        productType = order.productType
        if re.match(r"^(CNC|INTRADAY|MARGIN|MTF|CO|BO)$", productType, re.IGNORECASE):
            return productType.upper()
        else:
            logger.error(f"Invalid product type: {productType}")
            return "DELIVERY"

    @staticmethod
    def _getDuration(order: Order) -> str:
        """
        Get duration for Dhan order.

        :param order: The order object containing the duration
        :returns: 'DAY', 'IOC', 'GTC', or 'GTD'
        """
        allowed_durations = ['DAY', 'IOC', 'GTC', 'GTD']
        duration = order.duration.upper()

        if duration in allowed_durations:
            return duration
        else:
            logger.error(f"Invalid duration: {duration}. Defaulting to 'DAY'.")
            return "DAY"

    @staticmethod
    def _getAmoTime(order: Order) -> str:
        """Get amo time for dhan
            :returns 'OPEN' or 'OPEN_30' or 'OPEN_60'"""
        duration = order.amo
        if re.match(r"^(OPEN|OPEN_30|OPEN_60)$", duration, re.IGNORECASE):
            return duration.upper()
        else:
            logger.error(f"Invalid amo time: {duration}")
            return "OPEN"

    @staticmethod
    def _getLegName(order: Order) -> str:

        legName = "NA"
        legName = order.tradingSymbol
        if re.match(r"^(ENTRY_LEG|STOP_LOSS_LEG|TARGET_LEG|NA)$", legName, re.IGNORECASE):
            return legName.upper()
        else:
            logger.error(f"Invalid leg name: {legName}")
            return "NA"

    @staticmethod
    def _getExchangeSegment(order: Order) -> str | None:
        exch = order.segment
        if re.match(r"^(NSE_EQ|NSE_FNO|NSE_CURRENCY|BSE_EQ|BSE_FNO|BSE_CURRENCY|MCX_COMM)$", exch, re.IGNORECASE):
            return exch.upper()
        else:
            logger.error(f"Invalid exchange: {exch}")
            return None

    @staticmethod
    def _format_trading_symbol(symbol: str) -> str:
        """
        Remove '-EQ', '-BE', or '-BL' from the end of the trading symbol.

        :param symbol: The original trading symbol
        :return: The formatted trading symbol
        """
        suffixes_to_remove = ['-EQ', '-BE', '-BL']
        for suffix in suffixes_to_remove:
            if symbol.endswith(suffix):
                return symbol[:-len(suffix)]
        return symbol

    def _getSecurityId(self, order):
        symbol = order.tradingSymbol
        formatted_symbol = self._format_trading_symbol(symbol)
        security_id = getSecurityIdFromTradingSymbol(formatted_symbol.upper(), order.exchange.upper(), order.segment.upper())
        return security_id

    @staticmethod
    def _get_exchange_segment(order):
        """
        Convert exchange and segment to the format required by Dhan API.

        :param order
        :return: The formatted exchange segment string
        """
        exchange = order.exchange.upper()
        segment = order.segment.upper()

        if exchange == "NSE":
            if segment == "EQUITY":
                return "NSE_EQ"
            elif segment == "FNO":
                return "NSE_FNO"
            elif segment == "CURRENCY":
                return "NSE_CURRENCY"
        elif exchange == "BSE":
            if segment == "EQUITY":
                return "BSE_EQ"
            elif segment == "FNO":
                return "BSE_FNO"
            elif segment == "CURRENCY":
                return "BSE_CURRENCY"
        elif exchange == "MCX" and segment == "COMMODITY":
            return "MCX_COMM"

        raise ValueError(f"Invalid exchange-segment combination: {exchange}-{segment}")

    def generateConsent(self) -> str | None:
        print("generateConsent")
        response = self._getAuthRequest("api.generate.consent")
        if response is not None:
            if response["status"] == 0:
                return None
            else:
                return response["consentId"]
        else:
            None
     
    def generateConsentLoginUrl(self, consentId: str) -> str|None:
        return self._authUrl + self._routes["api.consent.login"] + "?consentId=" + consentId
    
    def consumeConsent(self, tokenId) -> dict | None:
        response = self._getAuthRequest("api.consume.consent", {"tokenId": tokenId})
        if response is not None and "accessToken" in response and "dhanClientId" in response:
            return {
                "accessToken": response["accessToken"],
                "dhanClientId": response["dhanClientId"]
            }
        return None

    def _get_correlation_id(self, order: Order) -> str:
        """
        Generate a correlation ID for the order.

        :param order: The order object
        :return: A correlation ID string of maximum 25 characters
        """
        current_time = datetime.now(timezone.utc)
        formatted_time = current_time.strftime("%Y%m%d%H%M%S%f")
        full_id = f"{formatted_time}_{order.tradingSymbol}_{self.client_id}"
        return full_id[-25:]

    def placeOrder(self, order: Order) -> Union[OrderResponse, ErrorResponse]:
        params = {
            "dhanClientId": self.client_id,
            "correlationId": self._get_correlation_id(order),
            "exchangeSegment": self._get_exchange_segment(order),
            "transactionType": self._getTransactionType(order),
            "productType": self._getProductType(order),
            "orderType": self._getOrderType(order),
            "validity": self._getDuration(order),
            "tradingSymbol": order.tradingSymbol,
            "securityId": self._getSecurityId(order),
            "quantity": int(order.quantity),
            "price": float(order.price),
            "disclosedQuantity": int(order.discQuantity),
            "triggerPrice": int(order.triggerPrice),
        }
            # "afterMarketOrder": true,  # these are to be used for when amo and derivatives are run
            # "amoTime": "OPEN",
            # "boProfitValue": -3.402823669209385e+38,
            # "boStopLossValue": -3.402823669209385e+38,
            # "drvExpiryDate": "string",
            # "drvOptionType": "CALL",
            # "drvStrikePrice": -3.402823669209385e+38

        try:
            response = self._postRequest("api.order.place", params)
            if response and response.get('status'):
                return self._parseOrderResponse(response, order)
            else:
                return ErrorResponse(
                    data=response.get('data', {}),
                    status=1,
                    message=response.get('message', "Error occurred while placing order"),
                    errorCode=response.get('errorCode', response.get('errorcode', "Unknown error"))
                )
        except Exception as e:
            return ErrorResponse(
                data={},
                status=1,
                message=f"Exception occurred while placing order: {str(e)}",
                errorCode="EXCEPTION"
            )

    def modifyOrder(self, order: Order, orderId: str) -> OrderResponse:
        params = {
            "dhanClientId": self.client_id,
            "order-id": str(orderId),
            "orderType": self._getOrderType(order),
            "legName": self._getLegName(order),
            "price": int(order.price),
            "quantity": order.quantity,
            "disclosedQuantity": order.discQuantity,
            "triggerPrice": "", #Change
            "validity": self._getDuration(order),
        }
        print("Modify order params")
        print(params)
        response = self._putRequest("api.order.modify", params)
        print(response)
        if response.get('status'):
            response = self._parseOrderResponse(response)
            return response
        else:
            '''when there is some issue in response, 'status' key goes missing, code gives keyError 
               and hence the below code is written to handle it.'''
            response = ErrorResponse(
                data=response.get('data', {}),
                status=1,
                message=response.get('message', "Error occurred while fetching order status"),
                errorCode=response.get('errorCode', response.get('errorcode', "Unknown error"))
            )
            return response 

    def cancelOrder(self, orderId: str) -> OrderResponse:
        print("cancelOrder")
        params = {
            "order-id": str(orderId),
        }
        print("Cancel order params")
        print(params)
        response = self._deleteRequest("api.order.cancel", params)
        print(response)
        if response.get('status'):
            response = self._parseOrderResponse(response)
            return response
        else:
            '''when there is some issue in response, 'status' key goes missing, code gives keyError 
               and hence the below code is written to handle it.'''
            response = ErrorResponse(
                data=response.get('data', {}),
                status=1,
                message=response.get('message', "Error occurred while fetching order status"),
                errorCode=response.get('errorCode', response.get('errorcode', "Unknown error"))
            )
            return response 

    def getOrderBook(self) -> OrderBookResponse:
        response = self._getRequest("api.order.book")
        print(response)
        if response is not None and type(response) == list:
            response = self._parseOrderBookResponse(response)
            return response
        else:
            '''when there is some issue in response, 'status' key goes missing, code gives keyError 
               and hence the below code is written to handle it.'''
            response = ErrorResponse(
                data=response.get('data', {}),
                status=1,
                message=response.get('message', "Error occurred while fetching order status"),
                errorCode=response.get('errorCode', response.get('errorcode', "Unknown error"))
            )
            return response
    
    def getTradeBook(self) -> TradeBookResponse:
        response = self._getRequest("api.trade.book")
        print(response)
        if response is not None and type(response) == list:
            response = self._parseTradeBookResponse(response)
            return response
        else:
            '''when there is some issue in response, 'status' key goes missing, code gives keyError 
               and hence the below code is written to handle it.'''
            response = ErrorResponse(
                data={},
                status=1,
                message="Error occurred while fetching trade book",
                errorCode=response.get('status_code')
            )
            return response
    
    def getHolding(self) -> HoldingResponse:
        response = self._getRequest("api.holding")
        if response is not None and type(response) == list:
            response = self._parseHoldingResponse(response)
            print("Success response")
            print(response)
            return response
        else:
            '''when there is some issue in response, 'status' key goes missing, code gives keyError 
               and hence the below code is written to handle it.'''
            response = ErrorResponse(
                data=response.get('data', {}),
                status=1,
                message=response.get('message', response.get("internalErrorMessage","Error occurred while fetching order status")),
                errorCode=response.get('errorCode', response.get('errorcode', "Unknown error"))
            )
            return response

    def getPosition(self) -> Union[PositionResponse, ErrorResponse]:
        response = self._getRequest("api.position")
        print("Position response:", response)

        if response is None:
            return ErrorResponse(
                data={},
                status=1,
                message="Error occurred while fetching positions",
                errorCode="NO_RESPONSE"
            )

        try:
            return self._parsePositionResponse(response)
        except Exception as e:
            print(f"Error in _parsePositionResponse: {str(e)}")
            return ErrorResponse(
                data={},
                status=1,
                message=f"Error occurred while parsing position response: {str(e)}",
                errorCode="PARSE_ERROR"
            )

    def getFunds(self):
        response = self._getRequest("api.funds")  # fund response
        if response is not None:
            print(response)
            return self._parseFundsResponse(response)  # match keys
        else:
            return {
                "data": {},
                "errorcode": "API_ERROR",
                "message": "Error while fetching funds",
                "status": False
            }

    def getOrderStatus(self, orderId) -> Union[OrderStatusResponse, ErrorResponse]:
        response = self._getRequest("api.order.status", {"order-id": orderId})
        print(response)
        if response and isinstance(response, list) and len(response) > 0:
            orderStatusResponse = self._parseOrderStatusResponse(response[0])
            return orderStatusResponse
        else:
            return ErrorResponse(
                data={},
                status=1,
                message=response.get('errorMessage', "Error occurred while fetching order status"),
                errorCode=response.get('errorCode', response.get('errorcode', "Unknown error"))
            )

    # def generateTpin(self):
    #     response = self._getRequest("api.edis.tpin")
    #     if response is not None:
    #         print(response)
    #         return

    @handle_parse_error
    def _parseOrderResponse(self, response, order) -> OrderResponse:
        """Parse the order response from the angelOne platform
            @param response: JSON response from the place order api
            @return: OrderResponse object
        """
        orderId = response["orderid"] if response["orderid"] is not None else ""
        symbol = None #Todo From DB
        status = response["orderStatus"]
        # message = response["message"] if response["status"] else "Error: " + response["errorcode"] + " " + response[
        #     "message"]
        message = "Your order status is " + response["status"]
        uniqueOrderId = 0

        orderResponse = OrderResponse(orderId, symbol, status, message, uniqueOrderId)
        return orderResponse

    @staticmethod
    @handle_parse_error
    def _parseFundsResponse(response):
        if response:
            data = {
                "availablecash": str(response["availabelBalance"]),
                "availableintradaypayin": str(response["availabelBalance"]),
                "availablelimitmargin": str(response["availabelBalance"]),
                "collateral": str(response["collateralAmount"]),
                "m2mrealized": "0.0000",
                "m2munrealized": "0.0000",
                "net": str(response["withdrawableBalance"]),
                "utiliseddebits": str(response["utilizedAmount"]),
                "utilisedexposure": None,
                "utilisedholdingsales": None,
                "utilisedoptionpremium": None,
                "utilisedpayout": str(response["blockedPayoutAmount"]),
                "utilisedspan": None,
                "utilisedturnover": None
            }
            return {
                "data": data,
                "errorcode": "",
                "message": "SUCCESS",
                "status": 0
            }
        else:
            return {
                "data": {},
                "errorcode": "NO_RESPONSE",
                "message": "Error occurred while fetching funds",
                "status": 1
            }

    @handle_parse_error
    def _parseOrderBookResponse(self, response) -> OrderBookResponse:
        orderBook = []

        if response is not None:
            for orderDetails in response:
                variety = None  # Not provided in the response
                orderType = orderDetails["orderType"]
                productType = orderDetails["productType"]
                duration = orderDetails["validity"]
                price = orderDetails["price"]
                quantity = orderDetails["quantity"]
                disclosedQuantity = orderDetails["disclosedQuantity"]
                symbol = orderDetails["tradingSymbol"]
                transactionType = orderDetails["transactionType"]
                exchange = orderDetails["exchangeSegment"].split('_')[0]  # Changed from '-' to '_'
                averagePrice = orderDetails["averageTradedPrice"]
                filledShares = orderDetails["filledQty"]
                unfilledShares = orderDetails["remainingQuantity"]
                orderId = orderDetails["orderId"]
                orderStatus = orderDetails["orderStatus"]
                orderStatusMessage = orderDetails[
                    "omsErrorDescription"]  # Changed from orderStatus to omsErrorDescription
                orderUpdateTime = orderDetails["updateTime"]
                lotsize = None  # Not provided in the response
                optionType = orderDetails["drvOptionType"]
                instrumentType = None  # Not provided in the response
                uniqueOrderId = orderDetails["exchangeOrderId"]  # Using exchangeOrderId as uniqueOrderId

                # Additional fields that you might want to include
                correlationId = orderDetails["correlationId"]
                createTime = orderDetails["createTime"]
                exchangeTime = orderDetails["exchangeTime"]
                triggerPrice = orderDetails["triggerPrice"]

                orderBookStructure = OrderBookStructure(
                    variety, orderType, productType, duration, price,
                    quantity, disclosedQuantity, symbol, transactionType,
                    exchange, averagePrice, filledShares, unfilledShares,
                    orderId, orderStatus, orderStatusMessage, orderUpdateTime,
                    lotsize, optionType, instrumentType, uniqueOrderId
                )

                # orderBookStructure.correlationId = correlationId
                # orderBookStructure.createTime = createTime
                # orderBookStructure.exchangeTime = exchangeTime
                # orderBookStructure.triggerPrice = triggerPrice

                orderBook.append(orderBookStructure)

        orderBookResponse = OrderBookResponse(
            0,
            "Order book fetched successfully",
            orderBook
        )

        return orderBookResponse

    @handle_parse_error
    def _parseTradeBookResponse(self, response) -> TradeBookResponse:
        tradeBook = []
        if response is not None:
            for tradeDetails in response:
                print(tradeDetails)
                exchange = tradeDetails["exchangeSegment"].split('_')[0]  # Extracting exchange from exchangeSegment
                productType = tradeDetails["productType"]
                symbol = tradeDetails["tradingSymbol"]
                multiplier = 1
                transactionType = tradeDetails["transactionType"]
                price = tradeDetails["tradedPrice"]
                filledShares = tradeDetails["tradedQuantity"]
                orderId = tradeDetails["orderId"]
                quantity = tradeDetails["tradedQuantity"]
                unfilledShares = 0

                # Additional fields that might be useful
                # exchangeOrderId = tradeDetails["exchangeOrderId"]
                # exchangeTradeId = tradeDetails["exchangeTradeId"]
                # orderType = tradeDetails["orderType"]
                # createTime = tradeDetails["createTime"]
                # updateTime = tradeDetails["updateTime"]
                # exchangeTime = tradeDetails["exchangeTime"]

                tradeBookStructure = TradeBookStructure(
                    exchange=exchange,
                    productType=productType,
                    symbol=symbol,
                    multiplier=multiplier,
                    transactionType=transactionType,
                    price=price,
                    filledShares=filledShares,
                    orderId=orderId,
                    quantity=quantity,
                    unfilledShares=unfilledShares
                )

                # tradeBookStructure.exchangeOrderId = exchangeOrderId
                # tradeBookStructure.exchangeTradeId = exchangeTradeId
                # tradeBookStructure.orderType = orderType
                # tradeBookStructure.createTime = createTime
                # tradeBookStructure.updateTime = updateTime
                # tradeBookStructure.exchangeTime = exchangeTime

                tradeBook.append(tradeBookStructure)

        tradeBookResponse = TradeBookResponse(
            0,
            "Trade book successfully fetched",
            tradeBook
        )

        return tradeBookResponse

    @handle_parse_error
    def _parseHoldingResponse(self, response) -> HoldingResponse:
        holding = []
        if response is not None:
            for holdingDetails in response:
                exchange = holdingDetails["exchange"]
                symbol = holdingDetails["tradingSymbol"]
                quantity = holdingDetails["totalQty"]
                ltp = None 
                pnl = None
                avgPrice = holdingDetails["avgCostPrice"]

                holdingStructure = HoldingResponseStructure(
                    symbol, exchange, quantity, ltp, pnl, avgPrice
                )
                holding.append(holdingStructure)

        else:
            return HoldingResponse(
                status=1,
                message="No data available",
                holding=[]
            )

        holdingResponse = HoldingResponse(
            0,
            "Holdings successfully fetched",
            holding
        )

        return holdingResponse

    @handle_parse_error
    def _parsePositionResponse(self, response) -> PositionResponse:
        positions = []
        if not isinstance(response, list):
            raise ValueError("Expected response to be a list")

        for positionDetails in response:
            try:
                position = PositionResponseStructure(
                    exchange=positionDetails["exchangeSegment"].split("_")[0],
                    symbol=positionDetails["tradingSymbol"],
                    name=positionDetails.get("symbolname", positionDetails["tradingSymbol"]),
                    multiplier=positionDetails["multiplier"],
                    buyQuantity=positionDetails["buyQty"],
                    sellQuantity=positionDetails["sellQty"],
                    buyAmount=positionDetails["dayBuyValue"],
                    sellAmount=positionDetails["daySellValue"],
                    buyAvgPrice=positionDetails["buyAvg"],
                    sellAvgPrice=positionDetails["sellAvg"],
                    netQuantity=positionDetails["netQty"]
                )
                positions.append(position)
            except KeyError as e:
                print(f"Missing key in position details: {str(e)}")
                continue

        return PositionResponse(
            status=0,
            message="Positions fetched successfully",
            position=positions
        )

    @handle_parse_error
    def _parseOrderStatusResponse(self, response) -> OrderStatusResponse:
        status = 1
        message = "Order fetched successfully"

        price = response["price"]
        quantity = response["quantity"]
        symbol = response["tradingSymbol"]
        exchange = response["exchangeSegment"].split("_")[0]
        filledShares = response["filledQty"]
        unfilledShares = response["remainingQuantity"]
        orderId = response["orderId"]
        orderStatus = response["orderStatus"]
        orderStatusMessage = response["omsErrorDescription"]
        orderUpdateTime = response["updateTime"]
        uniqueOrderId = orderId  # Set uniqueOrderId equal to orderId
        orderType = response["orderType"]
        productType = response["productType"]
        duration = response["validity"]
        disclosedQuantity = response["disclosedQuantity"]
        transactionType = response["transactionType"]
        averagePrice = response["averageTradedPrice"]
        lotsize = None  # Not provided in the response
        optionType = response["drvOptionType"]
        instrumentType = None  # Not provided in the response
        variety = None  # Not provided in the response

        correlationId = response.get("correlationId")
        if correlationId:
            message += f" (Correlation ID: {correlationId})"

        orderStatusResponse = OrderStatusResponse(
            status=status,
            message=message,
            price=price,
            quantity=quantity,
            symbol=symbol,
            exchange=exchange,
            filledShares=filledShares,
            unfilledShares=unfilledShares,
            orderId=orderId,
            orderStatus=orderStatus,
            orderStatusMessage=orderStatusMessage,
            orderUpdateTime=orderUpdateTime,
            uniqueOrderId=uniqueOrderId,
            orderType=orderType,
            productType=productType,
            duration=duration,
            disclosedQuantity=disclosedQuantity,
            transactionType=transactionType,
            averagePrice=averagePrice,
            lotsize=lotsize,
            optionType=optionType,
            instrumentType=instrumentType,
            variety=variety
        )

        return orderStatusResponse
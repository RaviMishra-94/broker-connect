import ssl
from urllib.parse import urljoin
import requests as req
import socket
import re, uuid
import logging
import json

import sys
sys.path.append('/Users/zolo/Projects/Freelance/broker-connect') # make dynnamic

from .dhan_scrip import getSecurityIdFromTradingSymbol

# Import other necessary modules for response and order handling
from body.Order import Order
from body.Response import OrderResponse, OrderBookResponse, TradeBookResponse, \
    OrderStatusResponse, HoldingResponse, PositionResponse, ErrorResponse, FundResponse, OrderBookStructure
from decorators import handle_parse_error

log = logging.getLogger(__name__)

class Dhan(object):

    #declaring constants
    NSE= 'NSE_EQ'
    BSE= 'BSE_EQ'
    CUR= 'NSE_CURRENCY'
    MCX= 'MCX_COMM'
    FNO= 'NSE_FNO'
    INDEX= 'IDX_I'
    NSE_FNO = 'NSE_FNO'
    BSE_FNO = 'BSE_FNO'
    BUY= B= 'BUY'
    SELL= S= 'SELL'
    CNC= 'CNC'
    INTRA= "INTRADAY"
    SL= "STOP_LOSS"
    SLM= "STOP_LOSS_MARKET"
    MARGIN= 'MARGIN'
    CO= 'CO'
    BO= 'BO'
    MTF= 'MTF'
    LIMIT= 'LIMIT'
    MARKET= 'MARKET'
    DAY= 'DAY'
    IOC= 'IOC'
    GTC= 'GTC'
    GTD= 'GTD'
    EQ= 'EQ'

    _rootUrl = "https://api.dhan.co"
    _default_timeout = 7  # seconds

    _routes = {
        # Order Management
        "api.order.place": "/v2/orders",  # Place a new order
        "api.order.modify": "/v2/orders/{order-id}",  # Modify existing order
        "api.order.cancel": "/v2/orders/{order-id}",  # Cancel order
        "api.order.book": "/v2/orders",  # Retrieve all orders of the day

        # Trade Book and Positions
        "api.trade.book": "/v2/trades",  # Fetch trade book
        "api.holding": "/v2/holdings",  # Get holdings
        "api.position": "/v2/positions",  # Get positions
        "api.funds": "/v2/fundlimit",  # Get fund details
        "api.order.status": "v2/orders/{order-id}" #Get order details/status
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

    def __init__(self, client_id, access_token=None, session_expiry_hook=None, debug=False, disable_ssl=False, timeout=7, proxies=None):
        self.access_token = access_token
        self.session_expiry_hook = session_expiry_hook
        self.debug = debug
        self.disable_ssl = disable_ssl
        self.timeout = timeout
        self.proxies = proxies
        self.client_id= str(client_id)

    def setSessionExpiryHook(self, method):
        """Set a custom session expiry hook."""
        if not callable(method):
            raise ValueError("Invalid input type. Only functions are accepted")
        self.session_expiry_hook = method

    # def login_url(self):
    #     """Generate the login URL for DhanHQ login flow."""
    #     return "%s?api_key=%s" % (self._login_url, self.api_key)


    def requestHeaders(self):
        headers = {"content-type": "application/json"}
        if self.access_token:
            headers["access-token"] = self.access_token
        return headers

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
        """Get duration for angel one
            :returns 'DAY' or 'IOC'"""
        duration = order.duration
        if re.match(r"^(DAY|IOC)$", duration, re.IGNORECASE):
            return duration.upper()
        else:
            logger.error(f"Invalid duration: {duration}")
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
        if re.match(r"^(ENTRY_LEG|STOP_LOSS_LEG|TARGET_LEG|NA)$", legName, re.IGNORECASE):
            return legName.upper()
        else:
            logger.error(f"Invalid leg name: {duration}")
            return "NA"

    @staticmethod
    def _getExchangeSegment(order: Order) -> str | None:
        exch = order.segment
        if re.match(r"^(NSE_EQ|NSE_FNO|NSE_CURRENCY|BSE_EQ|BSE_FNO|BSE_CURRENCY|MCX_COMM)$", exch, re.IGNORECASE):
            return exch.upper()
        else:
            logger.error(f"Invalid exchange: {exch}")
            return None

    def _getSecurityId(self, order):
        formatted_symbol = order.tradingSymbol
        securityId = getSecurityIdFromTradingSymbol(formatted_symbol, order.exchange)
        return str(int(securityId))
    
    @staticmethod
    def _getTradingSymbolFromOrder(order: Order) -> str:
        token = getSymbolFrom(order.tradingSymbol)   
        return symbol

    def placeOrder(self, order: Order) -> OrderResponse:
        params = {
            "dhanClientId": self.client_id,
            "transactionType": self._getTransactionType(order),
            "exchangeSegment": self._getExchangeSegment(order),
            "productType": self._getProductType(order),
            "orderType": self._getOrderType(order),
            "validity": self._getDuration(order),
            "securityId": self._getSecurityId(order),
            "quantity": order.quantity,
            "disclosedQuantity": order.discQuantity,
            "price": int(order.price),
            # "triggerPrice": int(order.price),
            # "afterMarketOrder": True,
            # "amoTime": "OPEN",
            # "boProfitValue": order.price,
            # "boStopLossValue": order.price
        }
        params["correlationId"] = "123abc678" #TODO to change from front end
        print("Place order params")
        print(params)
        response = self._postRequest("api.order.place", params)
        print("Place order server response")
        print(response)
        if response.get('status'):
            response = self._parseOrderResponse(response, order)
            return response
        else:
            '''when there is some issue in respone, 'status' key goes missing, code gives keyError 
               and hence the below code is written to handle it.'''
            response = ErrorResponse(
                data=response.get('data', {}),
                status=1,
                message=response.get('message', "Error occurred while fetching order status"),
                errorCode=response.get('errorCode', response.get('errorcode', "Unknown error"))
            )
            return response

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
            '''when there is some issue in respone, 'status' key goes missing, code gives keyError 
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
            '''when there is some issue in respone, 'status' key goes missing, code gives keyError 
               and hence the below code is written to handle it.'''
            response = ErrorResponse(
                data=response.get('data', {}),
                status=1,
                message=response.get('message', "Error occurred while fetching order status"),
                errorCode=response.get('errorCode', response.get('errorcode', "Unknown error"))
            )
            return response 

    def getOrderBook(self) -> OrderBookResponse:
        print("getOrderBook")
        response = self._getRequest("api.order.book")
        print("Response from server")
        print(response)
        if response is not None and type(response) == list:
            response = self._parseOrderBookResponse(response)
            print("Success response")
            print(response)
            return response
        else:
            '''when there is some issue in respone, 'status' key goes missing, code gives keyError 
               and hence the below code is written to handle it.'''
            response = ErrorResponse(
                data=response.get('data', {}),
                status=1,
                message=response.get('message', "Error occurred while fetching order status"),
                errorCode=response.get('errorCode', response.get('errorcode', "Unknown error"))
            )
            print("Failed response")
            print(response)
            return response
    
    def getTradeBook(self) -> TradeBookResponse:
        print("getTradeBook")
        response = self._getRequest("api.trade.book")
        print(response)
        if response is not None and type(response) == list:
            response = self._parseTradeBookResponse(response)
            return response
        else:
            '''when there is some issue in respone, 'status' key goes missing, code gives keyError 
               and hence the below code is written to handle it.'''
            response = ErrorResponse(
                data={},
                status=1,
                message="Error occurred while fetching trade book",
                errorCode=respone.status_code
            )
            return response
    
    def getHolding(self) -> HoldingResponse:
        print("getHolding")
        response = self._getRequest("api.holding")
        print(response)
        if response is not None and type(response) == list:
            response = self._parseHoldingResponse(response)
            print("Success response")
            print(response)
            return response
        else:
            '''when there is some issue in respone, 'status' key goes missing, code gives keyError 
               and hence the below code is written to handle it.'''
            response = ErrorResponse(
                data=response.get('data', {}),
                status=1,
                message=response.get('message', "Error occurred while fetching order status"),
                errorCode=response.get('errorCode', response.get('errorcode', "Unknown error"))
            )
            print("Failed response")
            print(response)
            return response

    def getPosition(self) -> PositionResponse:
        print("getPosition")
        response = self._getRequest("api.position")
        print(response)
        if response is not None:
            response = self._parsePositionResponse(response)
            return response
        else:
            '''when there is some issue in respone, 'status' key goes missing, code gives keyError 
               and hence the below code is written to handle it.'''
            response = ErrorResponse(
                data=response.get('data', {}),
                status=1,
                message=response.get('message', "Error occurred while fetching order status"),
                errorCode=response.get('errorCode', response.get('errorcode', "Unknown error"))
            )
            return response

    def getFunds(self):
        print("getFunds")
        response = self._getRequest("api.funds") # fund response
        if response is not None:
            response = self._parseFundResponse(response)
            print(response)
            return response
        else:
            response = ErrorResponse(
                data={},
                status=0,
                message="Error while fetching funds",
                errorCode=response.status_code
            )
            return response 
   
    def getOrderStatus(self, orderId) -> OrderStatusResponse:
        print("getOrderStatus of")
        print(orderId)
        response = self._getRequest("api.order.status", {"order-id": orderId})
        print(response)
        if response is not None and type(response) == list:
            orderStatusResponse = self._parseOrderStatusResponse(response[0])
            print("Success response")
            print(orderStatusResponse)
            return orderStatusResponse
        else:
           
            orderStatusResponse = ErrorResponse(
                data={},
                status=1,
                message=response.get('errorMessage', "Error occurred while fetching order status"),
                errorCode=response.get('errorCode', response.get('errorcode', "Unknown error"))
            )
            print("Failed response")
            print(orderStatusResponse)
            return orderStatusResponse
    
    @handle_parse_error
    def _parseOrderResponse(self, response, order) -> OrderResponse:
        """Parse the order response from the angelOne platform
            @param response: JSON response from the place order api
            @return: OrderResponse object
        """
        orderId = response["orderid"] if response["orderid"] is not None else ""
        symbol = None #Todo From DB
        status = respone["orderStatus"]
        # message = response["message"] if response["status"] else "Error: " + response["errorcode"] + " " + response[
        #     "message"]
        message = "Your order status is " + respone["status"]
        uniqueOrderId = 0

        orderResponse = OrderResponse(orderId, symbol, status, message, uniqueOrderId)
        return orderResponse

    @handle_parse_error
    def _parseFundResponse(self, response) -> FundResponse:
        
        availabelBalance = response["availabelBalance"]
        sodLimit = response["sodLimit"]
        collateralAmount = response["collateralAmount"]
        receiveableAmount = response["receiveableAmount"]
        utilizedAmount = response["utilizedAmount"]
        blockedPayoutAmount = response["blockedPayoutAmount"]
        withdrawableBalance = response["withdrawableBalance"]

        fundResponse = FundResponse(availabelBalance, sodLimit, collateralAmount, receiveableAmount, utilizedAmount, blockedPayoutAmount, withdrawableBalance)
        return fundResponse
   
    @handle_parse_error
    def _parseOrderBookResponse(self, response) -> OrderBookResponse:
        orderBook = []

        if (response is not None):
            for orderDetails in response:
                variety = None
                orderType = orderDetails["orderType"]
                productType = orderDetails["productType"]
                duration = orderDetails["validity"]
                price = orderDetails["price"]
                quantity = orderDetails["quantity"]
                disclosedQuantity = orderDetails["disclosedQuantity"]
                symbol = orderDetails["tradingSymbol"]
                transactionType = orderDetails["transactionType"]
                exchange = orderDetails["exchangeSegment"].split('-')[0]
                averagePrice = orderDetails["averageTradedPrice"]
                filledShares = None
                unfilledShares = None
                orderId = orderDetails["orderId"]
                orderStatus = orderDetails["orderStatus"]
                orderStatusMessage = orderDetails["orderStatus"]
                orderUpdateTime = orderDetails["updateTime"]
                lotsize = None
                optionType = None
                instrumentType = None
                uniqueOrderId = None

                orderBookStructure = OrderBookStructure(variety, orderType, productType, duration, price,
                                                        quantity, disclosedQuantity, symbol, transactionType,
                                                        exchange, averagePrice, filledShares, unfilledShares,
                                                        orderId, orderStatus, orderStatusMessage, orderUpdateTime,
                                                        lotsize, optionType, instrumentType, uniqueOrderId)
                orderBook.append(orderBookStructure)

        orderBookResponse = OrderBookResponse(
            1,
            "Order book fetched successfully",
            orderBook
        )

        return orderBookResponse

    @handle_parse_error
    def _parseTradeBookResponse(self, response) -> TradeBookResponse:
        tradeBook = []
        if (response is not None):
            for tradeDetails in response:
                print(tradeDetails)
                exchange = tradeDetails["exchangeOrderId"]
                productType = tradeDetails["productType"]
                symbol = tradeDetails["tradingSymbol"]
                multiplier = tradeDetails["multiplier"]
                transactionType = tradeDetails["transactionType"]
                price = tradeDetails["tradedPrice"],
                filledShares = None,
                orderId = tradeDetails["orderId"],
                quantity = tradeDetails["tradedQuantity"],
                unfilledShares = None

                tradeBookStructure = TradeBookStructure(
                    exchange, productType, symbol, multiplier, transactionType, price,
                    filledShares, orderId, quantity, unfilledShares
                )
                tradeBook.append(tradeBookStructure)

        tradeBookResponse = TradeBookResponse(
            "SUCCESS",
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
            0 if response["status"] else 1,
            response["message"],
            holding
        )

        return holdingResponse

    @handle_parse_error
    def _parsePositionResponse(self, response) -> PositionResponse:
        position = []
        if (response is not None):
            for positionDetails in response:
                exchange = positionDetails["exchangeSegment"].split("_")[0]
                symbol = positionDetails["tradingSymbol"]
                name = positionDetails["symbolname"] # TODO from Db
                multiplier = positionDetails["multiplier"]
                buyQuantity = positionDetails["buyQty"]
                sellQuantity = positionDetails["sellQty"]
                buyAmount = positionDetails["buyAvg"]
                sellAmount = positionDetails["sellAvg"]
                buyAvgPrice = positionDetails["buyAvg"]
                sellAvgPrice = positionDetails["sellAvg"]
                netQuantity = positionDetails["netQty"]

                positionResponseStructure = PositionResponseStructure(
                    exchange, symbol, name, multiplier, buyQuantity, sellQuantity, buyAmount,
                    sellAmount, buyAvgPrice, sellAvgPrice, netQuantity
                )
                position.append(positionResponseStructure)

        positionResponse = PositionResponse(
            1,
            "Positions fetched successfully",
            position
        )

        return positionResponse

    @handle_parse_error
    def _parseOrderStatusResponse(self, response) -> OrderStatusResponse:
        responseBody = response
        status = 1
        message = "Order fetched successfully"

        price = responseBody["price"]
        quantity = responseBody["quantity"]
        symbol = responseBody["tradingSymbol"]
        exchange = responseBody["exchangeSegment"].split("_")[0]
        filledShares = None
        unfilledShares = None
        orderId = responseBody["orderId"]
        orderStatus = responseBody["orderStatus"]
        orderStatusMessage = responseBody["omsErrorDescription"] # message in case of rejected
        orderUpdateTime = responseBody["updateTime"]
        uniqueOrderId = None
        orderType = responseBody["orderType"]
        productType = responseBody["productType"]
        duration = responseBody["validity"]
        disclosedQuantity = responseBody["disclosedQuantity"]
        transactionType = responseBody["transactionType"]
        averagePrice = responseBody["averageTradedPrice"]
        lotsize = None
        optionType = responseBody["drvOptionType"]
        instrumentType = None
        variety = None

        orderStatusResponse = OrderStatusResponse(status, message, price, quantity, symbol, exchange, filledShares,
                                                  unfilledShares, orderId, orderStatus, orderStatusMessage,
                                                  orderUpdateTime, uniqueOrderId, orderType, productType, duration,
                                                  disclosedQuantity, transactionType, averagePrice, lotsize, optionType,
                                                  instrumentType, variety)

        return orderStatusResponse

class DhanAuth:
    def __init__(self, partner_id, partner_secret, redirect_url):
        """
        Initialize the Dhan Auth Wrapper with partner credentials.
        :param partner_id: Partner's ID provided by Dhan.
        :param partner_secret: Partner's secret key provided by Dhan.
        :param redirect_url: Partner's redirect URL for the consent flow.
        """
        self.partner_id = partner_id
        self.partner_secret = partner_secret
        self.redirect_url = redirect_url
        self.base_url = "https://auth.dhan.co"
    
    def generate_consent(self):
        """
        Step 1: Generate the consent ID by sending partner credentials.
        :return: consent_id or None if the request fails.
        """
        url = f"{self.base_url}/partner/generate-consent"
        headers = {
            "partner_id": self.partner_id,
            "partner_secret": self.partner_secret
        }
        response = req.post(url, headers=headers)

        if response.status_code == 200:
            return response.json().get("consentId")
        else:
            print(f"Failed to generate consent. Status Code: {response.status_code}, Response: {response.text}")
            return None
    
    def consent_login_url(self, consent_id):
        """
        Step 2: Generate the consent login URL to redirect the user to Dhan's login page.
        :param consent_id: The consent ID obtained from the previous step.
        :return: The full URL where the user should be redirected.
        """
        return f"{self.base_url}/consent-login?consentId={consent_id}"
    
    def consume_consent(self, token_id):
        """
        Step 3: Fetch user details using the token ID received after the user logs in.
        :param token_id: The token ID received from the consent login step.
        :return: User details (JSON) or None if the request fails.
        """
        url = f"{self.base_url}/partner/consume-consent?tokenId={token_id}"
        headers = {
            "partner_id": self.partner_id,
            "partner_secret": self.partner_secret
        }
        response = req.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to consume consent. Status Code: {response.status_code}, Response: {response.text}")
            return None

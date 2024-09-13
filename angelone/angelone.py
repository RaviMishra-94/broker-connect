import ssl
from urllib.parse import urljoin

import requests as req
import socket
import re, uuid
import logzero
from logzero import logger
import logging
import json
import os
import time

from angelone.angelOne_scrip_master import get_token_id_from_symbol, get_token_and_exchange_from_symbol
from body.Order import Order
from body.Response import OrderResponse, OrderBookStructure, OrderBookResponse, TradeBookStructure, TradeBookResponse, \
    OrderStatusResponse, HoldingResponseStructure, HoldingResponse, PositionResponseStructure, PositionResponse, \
    ErrorResponse
from decorators import handle_parse_error

log = logging.getLogger(__name__)


class AngelOne(object):
    _rootUrl = "https://apiconnect.angelbroking.com"
    _login_url = "https://smartapi.angelbroking.com/publisher-login"
    _default_timeout = 7  # seconds

    _routes = {
        "api.login": "/rest/auth/angelbroking/user/v1/loginByPassword",
        "api.logout": "/rest/secure/angelbroking/user/v1/logout",
        "api.token": "/rest/auth/angelbroking/jwt/v1/generateTokens",
        "api.refresh": "/rest/auth/angelbroking/jwt/v1/generateTokens",
        "api.user.profile": "/rest/secure/angelbroking/user/v1/getProfile",

        "api.order.place": "/rest/secure/angelbroking/order/v1/placeOrder",
        "api.order.modify": "/rest/secure/angelbroking/order/v1/modifyOrder",
        "api.order.cancel": "/rest/secure/angelbroking/order/v1/cancelOrder",
        "api.order.book": "/rest/secure/angelbroking/order/v1/getOrderBook",

        "api.trade.book": "/rest/secure/angelbroking/order/v1/getTradeBook",
        "api.holding": "/rest/secure/angelbroking/portfolio/v1/getHolding",
        "api.allholding": "/rest/secure/angelbroking/portfolio/v1/getAllHolding",
        "api.position": "/rest/secure/angelbroking/order/v1/getPosition",
        "api.funds": "/rest/secure/angelbroking/user/v1/getRMS",
        "api.order.status": "/rest/secure/angelbroking/order/v1/details/{uniqueorderid}",
        "api.market.data": "rest/secure/angelbroking/market/v1/quote/",

        "api.option.greek": "/rest/secure/angelbroking/marketData/v1/optionGreek",
    }

    # Fetching local and public IP addresses and MAC address of the device
    try:
        clientPublicIp = " " + req.get('https://api.ipify.org').text
        if " " in clientPublicIp:
            clientPublicIp = clientPublicIp.replace(" ", "")
        hostname = socket.gethostname()
        clientLocalIp = socket.gethostbyname(hostname)
    except Exception as e:
        print(e)
    finally:
        clientPublicIp = "106.193.147.98"
        clientLocalIp = "127.0.0.1"
    clientMacAddress = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
    accept = "application/json"
    userType = "USER"
    sourceID = "WEB"

    def __init__(self, api_key=None, access_token=None, refresh_token=None, feed_token=None, userId=None, root=None,
                 debug=False, timeout=None, proxies=None, pool=None, disable_ssl=False, privateKey=None):
        self.debug = debug
        self.api_key = api_key
        self.session_expiry_hook = None
        self.disable_ssl = disable_ssl
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.feed_token = feed_token
        self.userId = userId
        self.proxies = proxies if proxies else {}
        self.root = root or self._rootUrl
        self.timeout = timeout or self._default_timeout
        self.Authorization = None
        self.clientLocalIP = self.clientLocalIp
        self.clientPublicIP = self.clientPublicIp
        self.clientMacAddress = self.clientMacAddress
        self.privateKey = api_key
        self.accept = self.accept
        self.userType = self.userType
        self.sourceID = self.sourceID

        # SSL Context creation
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.options |= ssl.OP_NO_TLSv1  # Disable TLS 1.0
        self.ssl_context.options |= ssl.OP_NO_TLSv1_1  # Disable TLS 1.1

        # Configure minimum TLS version to TLS 1.2
        self.ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2

        if not disable_ssl:
            self.reqsession = req.Session()
            if pool is not None:
                reqadapter = req.adapters.HTTPAdapter(**pool)
                self.reqsession.mount("https://", reqadapter)
            else:
                reqadapter = req.adapters.HTTPAdapter()
                self.reqsession.mount("https://", reqadapter)
            logger.info(f"in pool")
        else:
            # SSL disabled then use default ssl context
            self.reqsession = req

        # Create a log folder based on the current date
        log_folder = time.strftime("%Y-%m-%d", time.localtime())
        log_folder_path = os.path.join("ccxt_logs/angelOne_logs",
                                       log_folder)  # Construct the full path to the log folder
        os.makedirs(log_folder_path, exist_ok=True)  # Create the log folder if it doesn't exist
        log_path = os.path.join(log_folder_path, "app.log")  # Construct the full path to the log file
        logzero.logfile(log_path, loglevel=logging.ERROR)  # Output logs to a date-wise log file

        if pool:
            self.reqsession = req.Session()
            reqadapter = req.adapters.HTTPAdapter(**pool)
            self.reqsession.mount("https://", reqadapter)
            logger.info(f"in pool")
        else:
            self.reqsession = req

        # disable requests ssl warning
        req.packages.urllib3.disable_warnings()

    def requestHeaders(self):
        return {
            "Content-type": self.accept,
            "X-ClientLocalIP": self.clientLocalIp,
            "X-ClientPublicIP": self.clientPublicIp,
            "X-MACAddress": self.clientMacAddress,
            "Accept": self.accept,
            "X-PrivateKey": self.privateKey,
            "X-UserType": self.userType,
            "X-SourceID": self.sourceID
        }

    def setSessionExpiryHook(self, method):
        if not callable(method):
            raise ValueError("Invalid input type. Only functions are accepted")
        self.session_expiry_hook = method

    def login_url(self):
        """Get the remote login url to which a user should be redirected to initiate the login flow."""
        return "%s?api_key=%s" % (self._login_url, self.api_key)

    def _request(self, route, method, parameters=None):
        """Make an HTTP request"""
        params = parameters.copy() if parameters else {}

        uri = self._routes[route].format(**params)
        url = urljoin(self.root, uri)

        # Custom Headers
        headers = self.requestHeaders()

        # if self.access_token:
        #     #set authorisation header
        #     auth_header = self.access_token
        #     headers["Authorization"] = "Bearer {}".format(auth_header)

        if self.access_token:
            # set authorisation header
            if not self.access_token.startswith("Bearer "):
                self.access_token = "Bearer " + self.access_token
            headers["Authorization"] = self.access_token

        if self.debug:
            log.debug("Request: {method} {url} {params} {headers}".format(method=method, url=url, params=params,
                                                                          headers=headers))

        try:
            # print(json.dumps(params))
            # print(url)
            # print(headers)
            r = req.request(method,
                            url,
                            data=json.dumps(params) if method in ["POST", "PUT"] else None,
                            params=json.dumps(params) if method in ["GET", "DELETE"] else None,
                            headers=headers,
                            verify=not self.disable_ssl,
                            allow_redirects=True,
                            timeout=self.timeout,
                            proxies=self.proxies)

        except Exception as e:
            logger.error(
                f"Error occurred while making a {method} request to {url}. Headers: {headers}, Request: {params}, Response: {e}")
            raise e

        if self.debug:
            log.debug("Response: {code} {content}".format(code=r.status_code, content=r.content))

        # Validate content type
        if "json" in headers["Content-type"]:
            try:
                data = json.loads(r.content.decode("utf8"))

            except ValueError:
                raise ("Couldn't parse the JSON response received from the server: {content}".format(
                    content=r.content))

            return data

        elif "csv" in headers["Content-type"]:
            return r.content
        else:
            raise ("Unknown Content-type ({content_type}) with response: ({content})".format(
                content_type=headers["Content-type"],
                content=r.content))

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
        if re.match(r"^(MARKET|LIMIT|STOPLOSS_LIMIT|STOPLOSS_MARKET)$", orderType, re.IGNORECASE):
            return orderType.upper()
        else:
            logger.error(f"Invalid order type: {orderType}")
            return "LIMIT"

    @staticmethod
    def _getProductType(order: Order) -> str:
        """Get product type for angel one
            :returns INTRADAY|DELIVERY|CARRYFORWARD|MARGIN|BO"""
        productType = order.productType
        if re.match(r"^(INTRADAY|DELIVERY|CARRYFORWARD|MARGIN|BO)$", productType, re.IGNORECASE):
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
    def _getExchange(order: Order) -> str | None:
        """Get exchange for angel one
            :returns 'NSE' or 'BSE' or 'MCX - MCX Commodity' or 'NFO - NSE Future and Options' or
            'CDS - Currency Derivative Segment' or 'BFO - BSE Future or Options' or None"""
        exch = order.exchange
        if re.match(r"^(NSE|BSE|MCX|NFO|CDS|BFO)$", exch, re.IGNORECASE):
            return exch.upper()
        else:
            logger.error(f"Invalid exchange: {exch}")
            return None

    def _getSymbolToken(self, order):
        """Get symbol token for angel one"""
        formatted_symbol = self._getTradingSymbolFromOrder(order)
        token = get_token_id_from_symbol(formatted_symbol, order.exchange)
        return str(token)

    @staticmethod
    def _getTradingSymbolFromOrder(order: Order) -> str:
        return order.tradingSymbol

    @handle_parse_error
    def _parseOrderResponse(self, response) -> OrderResponse:
        """Parse the order response from the angelOne platform
            @param response: JSON response from the place order api
            @return: OrderResponse object
        """
        orderId = response["data"]["orderid"] if response["data"]["orderid"] is not None else ""
        try:
            symbol = response["data"]["script"] if response["data"]["script"] is not None else ""
        except:
            symbol = ""
        status = 0 if response["status"] else 1
        message = response["message"] if response["status"] else "Error: " + response["errorcode"] + " " + response[
            "message"]
        uniqueOrderId = response["data"]["uniqueorderid"] if response["data"]["uniqueorderid"] is not None else ""

        orderResponse = OrderResponse(orderId, symbol, status, message, uniqueOrderId)
        return orderResponse

    @handle_parse_error
    def _parseOrderBookResponse(self, response) -> OrderBookResponse:
        orderBook = []

        if (response["data"] is not None):
            for orderDetails in response["data"]:
                variety = orderDetails["variety"]
                orderType = orderDetails["ordertype"]
                productType = orderDetails["producttype"]
                duration = orderDetails["duration"]
                price = orderDetails["price"]
                quantity = orderDetails["quantity"]
                disclosedQuantity = orderDetails["disclosedquantity"]
                symbol = orderDetails["tradingsymbol"]
                transactionType = orderDetails["transactiontype"]
                exchange = orderDetails["exchange"]
                averagePrice = orderDetails["averageprice"]
                filledShares = orderDetails["filledshares"]
                unfilledShares = orderDetails["unfilledshares"]
                orderId = orderDetails["orderid"]
                orderStatus = orderDetails["status"]
                orderStatusMessage = orderDetails["text"]
                orderUpdateTime = orderDetails["exchorderupdatetime"]
                lotsize = orderDetails["lotsize"]
                optionType = orderDetails["optiontype"]
                instrumentType = orderDetails["instrumenttype"]
                uniqueOrderId = orderDetails["uniqueorderid"]

                orderBookStructure = OrderBookStructure(variety, orderType, productType, duration, price,
                                                        quantity, disclosedQuantity, symbol, transactionType,
                                                        exchange, averagePrice, filledShares, unfilledShares,
                                                        orderId, orderStatus, orderStatusMessage, orderUpdateTime,
                                                        lotsize, optionType, instrumentType, uniqueOrderId)
                orderBook.append(orderBookStructure)

        orderBookResponse = OrderBookResponse(
            response["status"],
            response["message"],
            orderBook
        )

        return orderBookResponse

    @handle_parse_error
    def _parseTradeBookResponse(self, response) -> TradeBookResponse:
        tradeBook = []
        if (response["data"] is not None):
            for tradeDetails in response["data"]:
                exchange = tradeDetails["exchange"]
                productType = tradeDetails["producttype"]
                symbol = tradeDetails["tradingsymbol"]
                multiplier = tradeDetails["multiplier"]
                transactionType = tradeDetails["transactiontype"]
                price = tradeDetails["fillprice"],
                filledShares = tradeDetails["fillsize"],
                orderId = tradeDetails["orderid"],
                quantity = None,
                unfilledShares = None

                tradeBookStructure = TradeBookStructure(
                    exchange, productType, symbol, multiplier, transactionType, price,
                    filledShares, orderId, quantity, unfilledShares
                )
                tradeBook.append(tradeBookStructure)

        tradeBookResponse = TradeBookResponse(
            response["status"],
            response["message"],
            tradeBook
        )

        return tradeBookResponse

    @handle_parse_error
    def _parseOrderStatusResponse(self, response) -> OrderStatusResponse:
        responseBody = response["data"]

        status = 0 if response["status"] else 1
        message = response["message"]

        price = responseBody["price"]
        quantity = responseBody["quantity"]
        symbol = responseBody["tradingsymbol"]
        exchange = responseBody["exchange"]
        filledShares = responseBody["filledshares"]
        unfilledShares = responseBody["unfilledshares"]
        orderId = responseBody["orderid"]
        orderStatus = responseBody["status"]
        orderStatusMessage = responseBody["text"]
        orderUpdateTime = responseBody["exchorderupdatetime"]
        uniqueOrderId = responseBody["uniqueorderid"]
        orderType = responseBody["ordertype"]
        productType = responseBody["producttype"]
        duration = responseBody["duration"]
        disclosedQuantity = responseBody["disclosedquantity"]
        transactionType = responseBody["transactiontype"]
        averagePrice = responseBody["averageprice"]
        lotsize = responseBody["lotsize"]
        optionType = responseBody["optiontype"]
        instrumentType = responseBody["instrumenttype"]
        variety = responseBody["variety"]

        orderStatusResponse = OrderStatusResponse(status, message, price, quantity, symbol, exchange, filledShares,
                                                  unfilledShares, orderId, orderStatus, orderStatusMessage,
                                                  orderUpdateTime, uniqueOrderId, orderType, productType, duration,
                                                  disclosedQuantity, transactionType, averagePrice, lotsize, optionType,
                                                  instrumentType, variety)

        return orderStatusResponse

    @handle_parse_error
    def _parseHoldingResponse(self, response) -> HoldingResponse:
        holding = []
        if response.get("data") or (response.get('message') and response.get('message').lower() == 'success'):
            for holdingDetails in response["data"]:
                exchange = holdingDetails["exchange"]
                symbol = holdingDetails["tradingsymbol"]
                quantity = holdingDetails["quantity"]
                ltp = holdingDetails["ltp"]
                pnl = holdingDetails["profitandloss"]
                avgPrice = holdingDetails["averageprice"]

                holdingStructure = HoldingResponseStructure(
                    symbol, exchange, quantity, ltp, pnl, avgPrice
                )
                holding.append(holdingStructure)

        else:
            return HoldingResponse(
                status=1,
                message=response.get("message", "No data available"),
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
        if (response["data"] is not None):
            for positionDetails in response["data"]:
                exchange = positionDetails["exchange"]
                symbol = positionDetails["tradingsymbol"]
                name = positionDetails["symbolname"]
                multiplier = positionDetails["multiplier"]
                buyQuantity = positionDetails["buyqty"]
                sellQuantity = positionDetails["sellqty"]
                buyAmount = positionDetails["buyamount"]
                sellAmount = positionDetails["sellamount"]
                buyAvgPrice = positionDetails["buyavgprice"]
                sellAvgPrice = positionDetails["sellavgprice"]
                netQuantity = positionDetails["netqty"]

                positionResponseStructure = PositionResponseStructure(
                    exchange, symbol, name, multiplier, buyQuantity, sellQuantity, buyAmount,
                    sellAmount, buyAvgPrice, sellAvgPrice, netQuantity
                )
                position.append(positionResponseStructure)

        positionResponse = PositionResponse(
            0 if response["status"] else 1,
            response["message"],
            position
        )

        return positionResponse

    def generateSession(self, clientCode, password, totp):

        params = {
            "clientcode": clientCode,
            "password": password,  # actually the pin
            "totp": totp
        }
        loginResponse = self._postRequest("api.login", params)

        if loginResponse['status'] == True:
            jwtToken = loginResponse['data']['jwtToken']
            self.access_token = jwtToken
            refreshToken = loginResponse['data']['refreshToken']
            feedToken = loginResponse['data']['feedToken']
            self.refresh_token = refreshToken
            self.feed_token = feedToken
            user = self.getProfile(refreshToken)

            id = user['data']['clientcode']
            self.userId = id
            user['data']['jwtToken'] = "Bearer " + jwtToken
            user['data']['refreshToken'] = refreshToken
            user['data']['feedToken'] = feedToken

            return user
        else:
            return loginResponse

    def terminateSession(self, clientCode):
        logoutResponse = self._postRequest("api.logout", {"clientcode": clientCode})
        return logoutResponse

    def generateToken(self, refreshToken):
        response = self._postRequest('api.token', {
            "refreshToken": refreshToken
        })
        if response.get('status'):
            jwtToken = response['data']['jwtToken']
            feedToken = response['data']['feedToken']
            self.access_token = jwtToken
            self.feed_token = feedToken
            return response
        else:
            '''when there is some issue in respone, 'status' key goes missing, codes gives keyError 
               and hence the below code is written to handle it.'''
            return response

    def renewAccessToken(self):
        response = self._postRequest('api.refresh', {
            "jwtToken": self.access_token,
            "refreshToken": self.refresh_token
        })

        tokenSet = {}

        if "jwtToken" in response:
            tokenSet['jwtToken'] = response['data']['jwtToken']
        else:
            return response

        tokenSet['clientcode'] = self.userId
        tokenSet['refreshToken'] = response['data']['refreshToken']

        return tokenSet

    def getProfile(self, refreshToken):
        user = self._getRequest("api.user.profile", {"refreshToken": refreshToken})
        return user

    @staticmethod
    def _getOrderVarietyFromOrder(order: Order):
        variety = order.orderVariety
        if re.match(r"NORMAL|AMO|ROBO|STOPLOSS", variety, re.IGNORECASE):
            return variety.upper()
        else:
            logger.error(f"Invalid order variety: {variety}")
            return "NORMAL"

    def placeOrder(self, order: Order) -> OrderResponse:
        params = {
            "variety": self._getOrderVarietyFromOrder(order),
            "tradingsymbol": self._getTradingSymbolFromOrder(order),
            "symboltoken": self._getSymbolToken(order),
            "transactiontype": self._getTransactionType(order),
            "exchange": self._getExchange(order),
            "ordertype": self._getOrderType(order),
            "producttype": self._getProductType(order),
            "duration": self._getDuration(order),
            "price": str(order.price),
            "quantity": str(order.quantity),
            "stoploss": str(order.stopLossPrice),
            "squareoff": "0"
        }
        response = self._postRequest("api.order.place", params)
        # if response is not None and response.get('status', False):
        #     if 'data' in response and response['data'] is not None and 'orderid' in response['data']:
        #         orderResponse = response
        #         return orderResponse
        #     else:
        #         logger.error(f"Invalid response format: {response}")
        # else:
        #     logger.error(f"API request failed: {response}")
        # return None
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

    def modifyOrder(self, order: Order, orderId: str) -> OrderResponse:
        params = {
            "variety": self._getOrderVarietyFromOrder(order),
            "orderid": str(orderId),
            "ordertype": self._getOrderType(order),
            "producttype": self._getProductType(order),
            "duration": self._getDuration(order),
            "price": str(order.price),
            "quantity": str(order.quantity),
            "tradingsymbol": self._getTradingSymbolFromOrder(order),
            "symboltoken": self._getSymbolToken(order),
            "exchange": self._getExchange(order)
        }
        response = self._postRequest("api.order.modify", params)
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

    def cancelOrder(self, variety: str, orderId: str) -> OrderResponse:
        params = {
            "variety": variety,
            "orderid": orderId
        }
        orderResponse = self._postRequest("api.order.cancel", params)
        if orderResponse.get('status'):
            orderResponse = self._parseOrderResponse(orderResponse)
            return orderResponse
        else:
            '''when there is some issue in respone, 'status' key goes missing, code gives keyError 
               and hence the below code is written to handle it.'''
            orderResponse = ErrorResponse(
                data=orderResponse.get('data', {}),
                status=1,
                message=orderResponse.get('message', "Error occurred while fetching order status"),
                errorCode=orderResponse.get('errorCode', orderResponse.get('errorcode', "Unknown error"))
            )
            return orderResponse

    def getOrderBook(self) -> OrderBookResponse:
        response = self._getRequest("api.order.book")
        if response.get('status'):
            response = self._parseOrderBookResponse(response)
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

    def getTradeBook(self) -> TradeBookResponse:
        response = self._getRequest("api.trade.book")
        if response.get('status'):
            response = self._parseTradeBookResponse(response)
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

    def getHolding(self) -> HoldingResponse:
        response = self._getRequest("api.holding")
        if response.get('status'):
            response = self._parseHoldingResponse(response)
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

    def getAllHolding(self):
        response = self._getRequest("api.allholding")
        if response.get('status'):
            total_holdings = response['data']['totalholding']
            total_holdings_response = {
                'totalHoldings': total_holdings,
                'message': "SUCCESS",
                'status': 0
            }
            return total_holdings_response
        else:
            '''when there is some issue in respone, 'status' key goes missing, code gives keyError 
               and hence the below code is written to handle it.'''
            response = {
                'data': response.get('data', {}),
                'status': 1,
                'message': response.get('message', "Error occurred while fetching order status"),
                'errorCode': response.get('errorCode', response.get('errorcode', "Unknown error"))
            }
            return response

    def getPosition(self) -> PositionResponse:
        response = self._getRequest("api.position")
        if response.get('status'):
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
        response = self._getRequest("api.funds")
        return response

    def getOrderStatus(self, uniqueorderid) -> OrderStatusResponse:
        response = self._getRequest("api.order.status", {"uniqueorderid": uniqueorderid})
        if response.get('status'):
            orderStatusResponse = self._parseOrderStatusResponse(response)
            return orderStatusResponse
        else:
            '''when there is some issue in respone, 'status' key goes missing, code gives keyError 
               and hence the below code is written to handle it.'''
            orderStatusResponse = ErrorResponse(
                data=response.get('data', {}),
                status=1,
                message=response.get('message', "Error occurred while fetching order status"),
                errorCode=response.get('errorCode', response.get('errorcode', "Unknown error"))
            )
            return orderStatusResponse

nltb = '\n\t' #newline with tab
nl = '\n' #newline
tb = '\t' #tab

class OrderResponse:
    def __init__(self, status, message, uniqueOrderId = None):
        self.status = status
        self.message = message
        self.uniqueOrderId = uniqueOrderId #this order id will be the one which is used to get the order status using the order status api in any broker

    def __repr__(self):
        return f"OrderResponse(status={self.status}, message={self.message}, uniqueOrderId={self.uniqueOrderId})"

    def to_dict(self):
        return {
            'status': self.status,
            'message': self.message,
            'uniqueOrderId': self.uniqueOrderId
        }

class OrderBookStructure:
    """OrderBookStructure class is used to store the order book details fetched from the getorderBook method."""
    def __init__(self,
                 variety,
                 orderType,
                 productType,
                 duration,
                 price,
                 quantity,
                 disclosedQuantity,
                 symbol,
                 transactionType,
                 exchange,
                 averagePrice,
                 filledShares,
                 unfilledShares,
                 orderId,
                 orderStatus,
                 orderStatusMessage,
                 orderUpdateTime,
                 lotsize,
                 optionType,
                 instrumentType,
                 uniqueOrderId):
        self.variety = variety
        self.orderType = orderType
        self.productType = productType
        self.duration = duration
        self.price = price
        self.quantity = quantity
        self.disclosedQuantity = disclosedQuantity
        self.symbol = symbol
        self.transactionType = transactionType
        self.exchange = exchange
        self.averagePrice = averagePrice
        self.filledShares = filledShares
        self.unfilledShares = unfilledShares
        self.orderId = orderId
        self.orderStatus = orderStatus
        self.orderStatusMessage = orderStatusMessage
        self.orderUpdateTime = orderUpdateTime
        self.lotsize = lotsize
        self.optionType = optionType
        self.instrumentType = instrumentType
        self.uniqueOrderId = uniqueOrderId

    def __repr__(self):
        return f"""{{
            variety={self.variety},
            orderType={self.orderType},
            productType={self.productType},
            duration={self.duration},
            price={self.price},
            quantity={self.quantity},
            disclosedQuantity={self.disclosedQuantity},
            symbol={self.symbol},
            transactionType={self.transactionType},
            exchange={self.exchange},
            averagePrice={self.averagePrice},
            filledShares={self.filledShares},
            unfilledShares={self.unfilledShares},
            orderId={self.orderId},
            orderStatus={self.orderStatus},
            orderStatusMessage={self.orderStatusMessage},
            orderUpdateTime={self.orderUpdateTime},
            lotsize={self.lotsize},
            optionType={self.optionType},
            instrumentType={self.instrumentType},
            uniqueOrderId={self.uniqueOrderId}
        }}"""
    
    def to_dict(self):
        return {
            'variety': self.variety,
            'orderType': self.orderType,
            'productType': self.productType,
            'duration': self.duration,
            'price': self.price,
            'quantity': self.quantity,
            'disclosedQuantity': self.disclosedQuantity,
            'symbol': self.symbol,
            'transactionType': self.transactionType,
            'exchange': self.exchange,
            'averagePrice': self.averagePrice,
            'filledShares': self.filledShares,
            'unfilledShares': self.unfilledShares,
            'orderId': self.orderId,
            'orderStatus': self.orderStatus,
            'orderStatusMessage': self.orderStatusMessage,
            'orderUpdateTime': self.orderUpdateTime,
            'lotsize': self.lotsize,
            'optionType': self.optionType,
            'instrumentType': self.instrumentType,
            'uniqueOrderId': self.uniqueOrderId
        }

class OrderBookResponse:
    """OrderBookResponse class is used to store the response of the getOrderBook method.
    It contains the following attributes:
    status: boolean
    message: str
    orderBook: OrderBookStructure[]
    """
    def __init__(self,
                 status,
                 message,
                 orderBook):
        self.status = status
        self.message = message
        self.orderBook = orderBook

    def __repr__(self):
        return f"OrderBookResponse({nl}status={self.status},{nl}message={self.message},{nl}orderBook={self.orderBook}{nl})"
    
    def to_dict(self):
        return {
            'status': self.status,
            'message': self.message,
            'orderBook': [trade.__dict__ for trade in self.orderBook]
        }
class TradeBookStructure:
    def __init__(self,
                 exchange,
                 productType,
                 symbol,
                 multiplier,
                 transactionType,
                 price,
                 filledShares,
                 orderId,
                 quantity,
                 unfilledShares):
        self.exchange = exchange
        self.productType = productType
        self.symbol = symbol
        self.multiplier = multiplier
        self.transactionType = transactionType
        self.price = price
        self.filledShares = filledShares
        self.orderId = orderId
        self.quantity = quantity
        self.unfilledShares = unfilledShares

    def __repr__(self):
        return f"""{{
            exchange={self.exchange},
            productType={self.productType},
            symbol={self.symbol},
            multiplier={self.multiplier},
            transactionType={self.transactionType},
            price={self.price},
            filledShares={self.filledShares},
            orderId={self.orderId},
            quantity={self.quantity},
            unfilledShares={self.unfilledShares}
        }}"""

    def to_dict(self):
        return {
            'exchange': self.exchange,
            'productType': self.productType,
            'symbol': self.symbol,
            'multiplier': self.multiplier,
            'transactionType': self.transactionType,
            'price': self.price,
            'filledShares': self.filledShares,
            'orderId': self.orderId,
            'quantity': self.quantity,
            'unfilledShares': self.unfilledShares
        }

class TradeBookResponse:
    def __init__(self,
                 status,
                 message,
                 tradeBook):
        self.status = status
        self.message = message
        self.tradeBook = tradeBook

    def __repr__(self):
        return f"TradeBookResponse({nl}status={self.status},{nl}message={self.message},{nl}tradeBook={self.tradeBook}{nl})"

    def to_dict(self):
        return {
            'status': self.status,
            'message': self.message,
            'tradeBook': [trade.__dict__ for trade in self.tradeBook]
        }

class OrderStatusResponse:
    def __init__(self,
                 status,
                 message,
                 price,
                 quantity,
                 symbol,
                 exchange,
                 filledShares,
                 unfilledShares,
                 orderId,
                 orderStatus,
                 orderStatusMessage,
                 orderUpdateTime,
                 uniqueOrderId,
                 orderType="",
                 productType="",
                 duration="",
                 disclosedQuantity="",
                 transactionType="",
                 averagePrice="",
                 lotsize="",
                 optionType="",
                 instrumentType="",
                 variety=""):
        self.status = status
        self.message = message
        self.variety = variety
        self.orderType = orderType
        self.productType = productType
        self.duration = duration
        self.price = price
        self.quantity = quantity
        self.disclosedQuantity = disclosedQuantity
        self.symbol = symbol
        self.transactionType = transactionType
        self.exchange = exchange
        self.averagePrice = averagePrice
        self.filledShares = filledShares
        self.unfilledShares = unfilledShares
        self.orderId = orderId
        self.orderStatus = orderStatus
        self.orderStatusMessage = orderStatusMessage
        self.orderUpdateTime = orderUpdateTime
        self.lotsize = lotsize
        self.optionType = optionType
        self.instrumentType = instrumentType
        self.uniqueOrderId = uniqueOrderId

    def __repr__(self):
        return f"""{{
            status={self.status},
            message={self.message},
            variety={self.variety},
            orderType={self.orderType},
            productType={self.productType},
            duration={self.duration},
            price={self.price},
            quantity={self.quantity},
            disclosedQuantity={self.disclosedQuantity},
            symbol={self.symbol},
            transactionType={self.transactionType},
            exchange={self.exchange},
            averagePrice={self.averagePrice},
            filledShares={self.filledShares},
            unfilledShares={self.unfilledShares},
            orderId={self.orderId},
            orderStatus={self.orderStatus},
            orderStatusMessage={self.orderStatusMessage},
            orderUpdateTime={self.orderUpdateTime},
            lotsize={self.lotsize},
            optionType={self.optionType},
            instrumentType={self.instrumentType},
            uniqueOrderId={self.uniqueOrderId}
        }}"""

    def to_dict(self):
        return {
            'status': self.status,
            'message': self.message,
            'variety': self.variety,
            'orderType': self.orderType,
            'productType': self.productType,
            'duration': self.duration,
            'price': self.price,
            'quantity': self.quantity,
            'disclosedQuantity': self.disclosedQuantity,
            'symbol': self.symbol,
            'transactionType': self.transactionType,
            'exchange': self.exchange,
            'averagePrice': self.averagePrice,
            'filledShares': self.filledShares,
            'unfilledShares': self.unfilledShares,
            'orderId': self.orderId,
            'orderStatus': self.orderStatus,
            'orderStatusMessage': self.orderStatusMessage,
            'orderUpdateTime': self.orderUpdateTime,
            'lotsize': self.lotsize,
            'optionType': self.optionType,
            'instrumentType': self.instrumentType,
            'uniqueOrderId': self.uniqueOrderId
        }

class HoldingResponseStructure:
    def __init__(self,
                 symbol,
                 exchange,
                 quantity,
                 ltp,
                 pnl,
                 avgPrice):
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.ltp = ltp
        self.pnl = pnl
        self.avgPrice = avgPrice

    def __repr__(self):
        return f"""{{
            symbol={self.symbol},
            exchange={self.exchange},
            quantity={self.quantity},
            ltp={self.ltp},
            pnl={self.pnl},
            avgPrice={self.avgPrice}
        }}"""

    def to_dict(self):
        return {
            'symbol': self.symbol,
            'exchange': self.exchange,
            'quantity': self.quantity,
            'ltp': self.ltp,
            'pnl': self.pnl,
            'avgPrice': self.avgPrice
        }

class HoldingResponse:
    def __init__(self,
                 status,
                 message,
                 holding):
        self.status = status
        self.message = message
        self.holding = holding

    def __repr__(self):
        return f"HoldingResponse({nl}status={self.status},{nl}message={self.message},{nl}holding={self.holding}{nl})"

    def to_dict(self):
        return {
            'status': self.status,
            'message': self.message,
            'holding': [holding.__dict__ for holding in self.holding]
        }

class PositionResponseStructure:
    def __init__(self,
                 exchange,
                 symbol,
                 name,
                 multiplier,
                 buyQuantity,
                 sellQuantity,
                 buyAmount,
                 sellAmount,
                 buyAvgPrice,
                 sellAvgPrice,
                 netQuantity):
        self.exchange = exchange
        self.symbol = symbol
        self.name = name
        self.multiplier = multiplier
        self.buyQuantity = buyQuantity
        self.sellQuantity = sellQuantity
        self.buyAmount = buyAmount
        self.sellAmount = sellAmount
        self.buyAvgPrice = buyAvgPrice
        self.sellAvgPrice = sellAvgPrice
        self.netQuantity = netQuantity

    def __repr__(self):
        return f"""{{
            exchange={self.exchange},
            symbol={self.symbol},
            name={self.name},
            multiplier={self.multiplier},
            buyQuantity={self.buyQuantity},
            sellQuantity={self.sellQuantity},
            buyAmount={self.buyAmount},
            sellAmount={self.sellAmount},
            buyAvgPrice={self.buyAvgPrice},
            sellAvgPrice={self.sellAvgPrice},
            netQuantity={self.netQuantity}
        }}"""

    def to_dict(self):
        return {
            'exchange': self.exchange,
            'symbol': self.symbol,
            'name': self.name,
            'multiplier': self.multiplier,
            'buyQuantity': self.buyQuantity,
            'sellQuantity': self.sellQuantity,
            'buyAmount': self.buyAmount,
            'sellAmount': self.sellAmount,
            'buyAvgPrice': self.buyAvgPrice,
            'sellAvgPrice': self.sellAvgPrice,
            'netQuantity': self.netQuantity
        }

class PositionResponse:
    def __init__(self,
                 status,
                 message,
                 position):
        self.status = status
        self.message = message
        self.position = position

    def __repr__(self):
        return f"PositionResponse({nl}status={self.status},{nl}message={self.message},{nl}position={self.position}{nl})"

    def to_dict(self):
        return {
            'status': self.status,
            'message': self.message,
            'position': [position.__dict__ for position in self.position]
        }
    
class ErrorResponse:
    def __init__(self,
                 status,
                 message,
                 errorCode,data):
        self.status = status
        self.message = message
        self.errorCode = errorCode
        self.data = data    

    def __repr__(self):
        return f"ErrorResponse({nl}status={self.status},{nl}message={self.message},{nl}errorCode={self.errorCode}{nl})"

    def to_dict(self):
        return {
            'status': self.status,
            'message': self.message,
            'errorCode': self.errorCode,
            'data': self.data
        }
    
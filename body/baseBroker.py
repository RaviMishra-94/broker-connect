from body.Order import Order
from body.Response import OrderResponse, OrderBookResponse, TradeBookResponse, OrderStatusResponse, HoldingResponse, \
    PositionResponse


class Broker:

    _routes = {}

    def _request(self, route, method, parameters=None):
        pass

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

    def _parseOrderResponse(self, response) -> OrderResponse:
        pass

    def _parseOrderBookResponse(self, response) -> OrderBookResponse:
        pass

    def _parseTradeBookResponse(self, response) -> TradeBookResponse:
        pass

    def _parseOrderStatusResponse(self, response) -> OrderStatusResponse:
        pass

    def _parseHoldingResponse(self, response) -> HoldingResponse:
        pass

    def _parsePositionResponse(self, response) -> PositionResponse:
        pass

    def placeOrder(self, order: Order) -> OrderResponse:
        pass

    def modifyOrder(self, order: Order, orderId: str) -> OrderResponse:
        pass

    def cancelOrder(self, variety: str, orderId: str) -> OrderResponse:
        pass

    def getOrderBook(self) -> OrderBookResponse:
        pass

    def getTradeBook(self) -> TradeBookResponse:
        pass

    def getHolding(self) -> HoldingResponse:
        pass

    def getPosition(self) -> PositionResponse:
        pass

    def getOrderStatus(self, uniqueorderid) -> OrderStatusResponse:
        pass


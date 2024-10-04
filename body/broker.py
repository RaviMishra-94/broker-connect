from abc import ABC, abstractmethod

from body.Order import Order


class Broker(ABC):
    @abstractmethod
    def requestHeaders(self):
        pass
    @abstractmethod
    def _request(self, route, method, params):
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
    @abstractmethod
    def placeOrder(self, order: Order):
        pass
    @abstractmethod
    def modifyOrder(self, order: Order):
        pass
    @abstractmethod
    def cancelOrder(self, order: Order):
        pass
    @abstractmethod
    def getOrderBook(self):
        pass
    @abstractmethod
    def getTradeBook(self):
        pass
    @abstractmethod
    def getHolding(self):
        pass
    @abstractmethod
    def getPosition(self):
        pass
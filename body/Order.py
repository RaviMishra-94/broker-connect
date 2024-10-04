from body.enums import Exchange, TransactionType, Segment


class Order:
    def __init__(self, exchange="NSE", segment="CASH", price=0.0, transactionType="BUY", quantity=0, discQuantity=0,
                 stopLossPrice=0.0, tradingSymbol="", orderVariety="NORMAL", orderType="LIMIT", productType="DELIVERY",
                 duration="DAY", isin=None, uniqueOrderId="", validTillDate=None, AfterHours="N",
                 triggerPrice=0.0):
        self.exchange = exchange
        self.segment = segment
        self.price = price
        self.transactionType = transactionType
        self.quantity = quantity
        self.discQuantity = discQuantity
        self.stopLossPrice = stopLossPrice
        self.tradingSymbol = tradingSymbol
        self.orderVariety = orderVariety
        self.orderType = orderType
        self.productType = productType
        self.duration = duration
        self.isin = isin
        self.uniqueOrderId = uniqueOrderId
        self.validTillDate = validTillDate
        self.afterHours = AfterHours
        self.triggerPrice = triggerPrice

class BOCOOrder:
    symbol = "",
    isin = "",
    exchange = Exchange.NSE,
    transactionType = TransactionType.BUY,  #Buy Sell
    quantity = 0,
    segment = Segment.EQUITY,
    discQuantity = 0,
    isAtMarket = False,
    limitPriceInitialOrder = 0.0,
    triggerPriceInitialOrder = 0.0,
    limitPriceProfitOrder = 0.0,
    limitPriceForSL = 0.0,
    triggerPriceForSL = 0.0,
    trailingSL = 0.0,
    isStopLoss = False,

    def __init__(self
                 , symbol
                 , isin
                 , exchange: Exchange
                 , transactionType: TransactionType
                 , quantity
                 , segment: Segment
                 , discQuantity
                 , isAtMarket
                 , limitPriceInitialOrder
                 , triggerPriceInitialOrder
                 , limitPriceProfitOrder
                 , limitPriceForSL
                 , triggerPriceForSL
                 , trailingSL
                 , isStopLoss
                 ):
        self.symbol = symbol
        self.isin = isin
        self.exchange = exchange
        self.transactionType = transactionType
        self.quantity = quantity
        self.segment = segment
        self.discQuantity = discQuantity
        self.isAtMarket = isAtMarket
        self.limitPriceInitialOrder = limitPriceInitialOrder
        self.triggerPriceInitialOrder = triggerPriceInitialOrder
        self.limitPriceProfitOrder = limitPriceProfitOrder
        self.limitPriceForSL = limitPriceForSL
        self.triggerPriceForSL = triggerPriceForSL
        self.trailingSL = trailingSL
        self.isStopLoss = isStopLoss
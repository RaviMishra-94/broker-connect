
from dhan import Dhan
from body.Order import Order

def dhanAuthApi():
    dhan_auth = Dhan(partner_id="your_partner_id", partner_secret="your_partner_secret", redirect_url="your_redirect_url")
    # Step 1: Generate the consent ID
    consentId = dhan_auth.generateConsent()
    print(consentId)

    if consentId is not None:
        print(f"Consent ID: {consentId}")

        # Step 2: Redirect user to this URL for login
        consentLoginUrl = dhan_auth.generateConsentLoginUrl(consentId)
        print(f"Redirect user to: {consentLoginUrl}")

        # After the user logs in and is redirected to your server, capture the token_id from the URL
        # Assume token_id is captured from the URL here
        tokenId = "captured_token_id_from_redirect"

        # Step 3: Fetch user details using the token_id
        userDetails = dhan_auth.consumeConsent(tokenId)

        if userDetails is not None:
            print(f"User details: {user_details}")
        else:
            print("Failed to fetch user details.")
    else:
        print("Failed to generate consent ID.")

def dhanApi():
    # Example usage:
    # Instantiate the client with your API key and optionally the access token
    orderId = '2124091657672'
    dhan = Dhan(debug=True, access_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzMxNTE0MzkwLCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiaHR0cHM6Ly93d3cuaWFtY2xlYXJtaW5kLmNvbS8iLCJkaGFuQ2xpZW50SWQiOiIxMTA0NDU3ODk0In0.4ULUnS0x-eeDH4NiW-fdvEvNZ8mj4s--EEjTu8qyKRIzWML3WL2hicIvzsAks5KVYsuPujYDgvBCuDiSk0gs7Q", client_id="1104457894" )
    # dhan.getTradeBook()
    # dhan.getOrderBook()
    # dhan.getHolding()
    # dhan.getPosition()
    # dhan.getFunds()
    # dhan.getOrderStatus(orderId)
    # dhan.cancelOrder(orderId)
    order = Order(
        exchange="NSE",  # Use appropriate enum values
        segment="NSE_EQ",  # Use appropriate enum values
        price=0.0,
        transactionType="BUY",  # Use appropriate enum values
        quantity=1,
        discQuantity=0,
        # stopLossPrice=145.0,
        tradingSymbol="TCS",
        # orderVariety="NORMAL",
        orderType="MARKET",
        productType="INTRADAY",
        duration="DAY"
        # isin="US0378331005",
        # uniqueOrderId="1234567890",
        # validTillDate=None,  # Use a datetime object if needed
        # AfterHours="N",
        # triggerPrice=0.0
    )

    # dhan.placeOrder(order)
    # dhan.modifyOrder(order, orderId)
    dhan.generateTpin()

    # print(order)


if __name__ == "__main__":
    dhanApi()

# import requests
#
#
# def get_holdings(access_token):
#     url = "https://api.dhan.co/holdings"
#
#     headers = {
#         "Content-Type": "application/json",
#         "access-token": access_token
#     }
#
#     response = requests.get(url, headers=headers)
#
#     if response.status_code == 200:
#         return response.json()
#     else:
#         return f"Error: {response.status_code}, {response.text}"
#
#
# # Replace 'YOUR_ACCESS_TOKEN' with your actual token
# access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzI4OTEzNjM2LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwNDQ1Nzg5NCJ9.VisZOpiLMfImo7uXVHpmqWUr9vnRMEkxDOj7qZjT_svfjB_0VsLF6fYjt50SYYmO-XEhScph90nJTQp_WbNUvA"
#
# result = get_holdings(access_token)
# print(result)
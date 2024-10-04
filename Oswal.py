import hashlib
import requests
import json
class Oswal:
    _rootUrl = "https://openapi.motilaloswal.com"
    _default_timeout = 7  # seconds

    _routes = {
        "api.login": "/rest/login/v3/authdirectapi",
        "api.logout": "/rest/login/v1/logout",
        "api.token": "/rest/auth/angelbroking/jwt/v1/generateTokens",
        "api.refresh": "/rest/auth/angelbroking/jwt/v1/generateTokens",
        "api.user.profile": "/rest/login/v1/getprofile",
        "api.order.place": "/rest/trans/v1/placeorder",
        "api.order.modify": "/rest/trans/v2/modifyorder",
        "api.order.cancel": "/rest/trans/v1/cancelorder",
        "api.order.book": "/rest/book/v2/getorderbook",
        "api.trade.book": "/rest/book/v1/gettradebook",
        "api.holding": "/rest/report/v1/getdpholding",
        "api.position": "/rest/book/v1/getposition",
        "api.funds": "/rest/secure/angelbroking/user/v1/getRMS",
        "api.order.status": "/rest/book/v2/getorderdetailbyuniqueorderid",
        "api.trade.status": "/rest/book/v1/gettradedetailbyuniqueorderid",
    }

    def __init__(self, api_key, client_code, token=None,uniqueorderid = None, public_ip="1.2.3.4", local_ip="1.2.3.4", mac_address="00:00:00:00:00:00", browser_name="Chrome", browser_version="105.0"):
        self.api_key = api_key
        self.client_code = client_code
        self.auth_token = token
        self.local_ip = '192.168.1.73'
        self.public_ip = '27.34.59.143'
        self.mac_address = '28-CD-C4-58-2D-A2'
        self.browser_name = browser_name
        self.browser_version = browser_version
        self.uniqueorderid = uniqueorderid

    def get_url(self, api_name):
        return f"{self._rootUrl}{self._routes[api_name]}"

    def get_header(self):
         headers = {
            "Accept": "application/json",
            "User-Agent": "MOSL/V.1.1.0",
            "Authorization": self.auth_token,  # Include AuthToken here
            "ApiKey": self.api_key,
            "ClientLocalIp": self.local_ip,
            "ClientPublicIp": self.public_ip,
            "MacAddress": self.mac_address,
            "SourceId": "WEB",
            "vendorinfo": self.client_code,  # Assuming you are a client
            "osname": "Windows 11",
            "osversion": "10.0.19041",
            "devicemodel": "AHV",
            "manufacturer": "DELL",
            "productname": "Testing",
            "productversion": "V.1.1.0",
            "browsername": "Chrome",
            "browserversion": "105.0",
            "userid": self.client_code,
            "uniqueorderid":self.uniqueorderid
        }
         return headers
    
    def login(self, password, two_fa,totp):
        login_url = self.get_url("api.login")

        # Hash the password with API key
        hashed_password = hashlib.sha256((password + self.api_key).encode("utf-8")).hexdigest()

        headers = self.get_header()  # Initial headers for login
        post_data = {
            "userid": self.client_code,
            "password": hashed_password,
            "2FA": two_fa,
            'totp':totp
        }

        try:
            response = requests.post(login_url, headers=headers, json=post_data, timeout=self._default_timeout)
            response.raise_for_status()  # Check for HTTP error
            response_data = response.json()

            if response_data.get("status") == "SUCCESS":
                self.auth_token = response_data["AuthToken"].strip()
                print("Login successful, Auth Token:", self.auth_token)

                # Step 2: Check if OTP is required
                if response_data.get("isAuthTokenVerified") == "FALSE":
                    otp = input("Enter the OTP sent to your mobile: ")

                    # Prepare headers for OTP verification, now including the AuthToken
                    otp_headers = {
                        **headers,  # Include the original headers
                        "Authorization": f"{self.auth_token}"  # Correctly format the AuthToken
                    }

                    otp_post_data = {
                        "otp": otp
                    }

                    otp_url = "https://openapi.motilaloswal.com/rest/login/v3/verifyotp"
                    otp_response = requests.post(otp_url, headers=otp_headers, json=otp_post_data, timeout=self._default_timeout)
                    otp_response_data = otp_response.json()  # Parse the response to JSON

                    if otp_response_data.get("status") == "SUCCESS":
                        print("OTP verification successful, Auth Token is now valid.")
                        return otp_response_data
                    else:
                        print("OTP verification failed:", otp_response_data.get("message"))
                        return otp_response_data
                else:
                    print("Login Successful without OTP verification.")
                    return response_data

            else:
                self.write_into_log("FAILED", "OswalAPI", response_data.get("message", "Login failed"))
                return response_data

        except requests.exceptions.RequestException as e:
            self.write_into_log("FAILED", "OswalAPI", str(e))
            return {"status": "FAILED", "message": str(e)}


    def logout(self):
        if not self.auth_token:
            return {"status": "ERROR", "message": "Auth token is missing"}

        l_URL = self._rootUrl + self._routes["api.logout"]
        headers = {
            "Accept": "application/json",
            "User-Agent": "MOSL/V.1.1.0",
            "Authorization": self.auth_token,  # Use the auth token from login
            "ApiKey": self.api_key,
            "ClientLocalIp": self.local_ip,
            "ClientPublicIp": self.public_ip,
            "MacAddress": self.mac_address,
            "SourceId": "WEB",
            "osname": "Windows 10",
            "osversion": "10.0.19041",
            "browsername": "Chrome",
            "browserversion": "105.0"
        }
        
        l_PostData = {
            "userid": self.client_code  # Use client code for logout
        }

        try:
            # Send the request (assuming a requests library)
            response = requests.post(l_URL, json=l_PostData, headers=headers)
            
            if response.status_code == 200:
                return response.json()  # Return the parsed JSON response
            else:
                return {"status": "ERROR", "message": "Logout request failed", "errorcode": response.status_code}

        except Exception as e:
            return {"status": "FAILED", "message": str(e)}
        

    def GetProfile(self, f_strclientcode=None):
        # # WriteIntoLog("SUCCESS", "MOFSLOPENAPI.py", "Initialize GetProfile request send")
        l_GetProfileResponse = {}

        # Check if auth_token is set
        if not self.auth_token:
            return {"status": "FAILED", "message": "Auth token is not available", "errorcode": "MO9999"}

        headers = {
        "Accept": "application/json",
        "Authorization":self.auth_token,  # Prepend with 'Bearer ' if required by API
        "User-Agent": "MOSL/V.1.1.0",
        "ApiKey": self.api_key,
        "ClientLocalIp": self.local_ip,
        "ClientPublicIp": self.public_ip,
        "MacAddress": self.mac_address,
        "SourceId": "WEB",
        "vendorinfo": self.client_code,  # Assuming you are a client
        "osname": "Windows 11",
        "osversion": "10.0.19041",
        "devicemodel": "AHV",
        "manufacturer": "DELL",
        "productname": "Testing",
        "productversion": "V.1.1.0",
        "browsername": "Chrome",
        "browserversion": "105.0",
        "userid":self.client_code
         }

        try:
            l_strApiUrl = self._rootUrl + self._routes["api.user.profile"]
            l_strGetdata = {
                "clientcode": f_strclientcode or self.client_code
            }

            print("Profile Request URL:", l_strApiUrl)
            print("Profile Request Headers:", headers)
            print("Profile Request Data:", l_strGetdata)

            # Change to POST request if required by the API
            response = requests.post(l_strApiUrl, headers=headers, json=l_strGetdata)  # Use json parameter for POST body
            l_strJSON = response.text
            
            print("Profile Response Status Code:", response.status_code)
            print("Profile Response JSON:", l_strJSON)

            if response.status_code == 200:
                l_strDICT = json.loads(l_strJSON)
                # # WriteIntoLog("SUCCESS", "MOFSLOPENAPI.py", "GetProfile request sent successfully")
                l_GetProfileResponse = l_strDICT
            else:
                # # WriteIntoLog("FAILED", "MOFSLOPENAPI.py", l_strJSON)
                l_GetProfileResponse["status"] = "FAILED"
                l_GetProfileResponse["message"] = l_strJSON
                l_GetProfileResponse["errorcode"] = "" 
                l_GetProfileResponse["data"] = {"null"}

        except Exception as e:
            # # WriteIntoLog("FAILED", "MOFSLOPENAPI.py", str(e)) 
            l_GetProfileResponse["status"] = "FAILED"
            l_GetProfileResponse["message"] = str(e)
            l_GetProfileResponse["errorcode"] = ""  
            l_GetProfileResponse["data"] = {"null"}

        return l_GetProfileResponse
    
    def validate_auth_token(self):
    # After login, validate the AuthToken by calling the user profile API
        profile_url = self.get_url("api.user.profile")
        headers = self.get_header()  # AuthToken should be in the header
        
        try:
            # Change method to POST as the error suggests the method GET might not be allowed
            response = requests.post(profile_url, headers=headers, timeout=self._default_timeout)
            response.raise_for_status()
            profile_data = response.json()

            if profile_data.get("status") == "SUCCESS":
                print("AuthToken is valid.")
            else:
                print("AuthToken validation failed:", profile_data.get("message", "Validation failed"))

            return profile_data

        except requests.exceptions.RequestException as e:
            print("AuthToken validation error:", str(e))
            return {"status": "FAILED", "message": str(e)}

    def GetOrderBook(self):
        # WriteIntoLog("SUCCESS", "MOFSLOPENAPI.py", "Initialize GetOrderBook request sent")
        l_OrderBookResponse = {}

        headers =self.get_header()

        try:
            l_strApiUrl = self._rootUrl + self._routes["api.order.book"]  # Use the order book route
            l_strGetdata = {
                "clientcode":"NAO791" 
            }  # Assuming this is a dictionary of the necessary data

            # Change to POST request if required by the API
            response = requests.post(l_strApiUrl, headers=headers, json=l_strGetdata)  # Use json parameter for POST body
            l_strJSON = response.text

            if response.status_code == 200:
                l_strDICT = json.loads(l_strJSON)
                # WriteIntoLog("SUCCESS", "MOFSLOPENAPI.py", "GetOrderBook request sent successfully")
                l_OrderBookResponse = l_strDICT
            else:
                # WriteIntoLog("FAILED", "MOFSLOPENAPI.py", l_strJSON)
                l_OrderBookResponse["status"] = "FAILED"
                l_OrderBookResponse["message"] = l_strJSON
                l_OrderBookResponse["errorcode"] = "" 
                l_OrderBookResponse["data"] = {"null"}

        except Exception as e:
            # WriteIntoLog("FAILED", "MOFSLOPENAPI.py", str(e)) 
            l_OrderBookResponse["status"] = "FAILED"
            l_OrderBookResponse["message"] = str(e)
            l_OrderBookResponse["errorcode"] = ""  
            l_OrderBookResponse["data"] = {"null"}

        return l_OrderBookResponse

    def GetTradeBook(self,client_code):
        
        trade_book_response = {}

        try:
            # Prepare the request headers
            headers =self.get_header()

            # Prepare the request data
            request_data = {
                "clientcode": client_code
            }

            # Make the API call
            response = requests.post(self._rootUrl + self._routes["api.trade.book"], headers=headers, json=request_data)

            # Check the response status
            if response.status_code == 200:
                # Parse the JSON response
                trade_book_response = response.json()
               
            else:
                # Log the error response
               
                trade_book_response["status"] = "FAILED"
                trade_book_response["message"] = response.text
                trade_book_response["errorcode"] = response.status_code
                trade_book_response["data"] = {"null"}

        except Exception as e:
            # Handle exceptions during the request process
            

            trade_book_response["status"] = "FAILED"
            trade_book_response["message"] = str(e)
            trade_book_response["errorcode"] = ""
            trade_book_response["data"] = {"null"}

        return trade_book_response

    def GetOrderDetails(self):
        
        order_detail_response = {}

        try:
            # Prepare the request headers
            headers =self.get_header()

            # Prepare the request data
            request_data = {
                "clientcode": self.client_code,
                "uniqueorderid":self.uniqueorderid
            }

            # Make the API call
            response = requests.post(self._rootUrl + self._routes["api.order.status"], headers=headers, json=request_data)

            # Check the response status
            if response.status_code == 200:
                # Parse the JSON response
                order_detail_response = response.json()
               
            else:
                # Log the error response
               
                order_detail_response["status"] = "FAILED"
                order_detail_response["message"] = response.text
                order_detail_response["errorcode"] = response.status_code
                order_detail_response["data"] = {"null"}

        except Exception as e:
            # Handle exceptions during the request process
            

            order_detail_response["status"] = "FAILED"
            order_detail_response["message"] = str(e)
            order_detail_response["errorcode"] = ""
            order_detail_response["data"] = {"null"}

        return order_detail_response
    
    def GetTradeDetails(self):
        
        trade_detail_response = {}

        try:
            # Prepare the request headers
            headers =self.get_header()

            # Prepare the request data
            request_data = {
                "clientcode": self.client_code,
                "uniqueorderid":self.uniqueorderid
            }

            # Make the API call
            response = requests.post(self._rootUrl + self._routes["api.trade.status"], headers=headers, json=request_data)

            # Check the response status
            if response.status_code == 200:
                # Parse the JSON response
                trade_detail_response = response.json()
               
            else:
                # Log the error response
               
                trade_detail_response["status"] = "FAILED"
                trade_detail_response["message"] = response.text
                trade_detail_response["errorcode"] = response.status_code
                trade_detail_response["data"] = {"null"}

        except Exception as e:
            # Handle exceptions during the request process
            

            trade_detail_response["status"] = "FAILED"
            trade_detail_response["message"] = str(e)
            trade_detail_response["errorcode"] = ""
            trade_detail_response["data"] = {"null"}

        return trade_detail_response
    

    def GetHoldings(self):
        
        holding_response = {}
        # Prepare the request headers
        headers =self.get_header()

        # Prepare the request data
        request_data = {
            "clientcode": self.client_code,
            
        }

        # Make the API call
        response = requests.post(self._rootUrl + self._routes["api.holding"], headers=headers, json=request_data)

        # Check the response status
        if response.status_code == 200:
            # Parse the JSON response
            holding_response = response.json()
            
        else:
            holding_response = {'err':"Got Error"}

        return holding_response


    def GetPosition(self):
        
        position_response = {}
        # Prepare the request headers
        headers =self.get_header()

        # Prepare the request data
        request_data = {
            "clientcode": self.client_code,
            
        }

        # Make the API call
        response = requests.post(self._rootUrl + self._routes["api.position"], headers=headers, json=request_data)

        # Check the response status
        if response.status_code == 200:
            # Parse the JSON response
            position_response = response.json()
            
        else:
            position_response = {'err':"Got Error"}

        return position_response


    def PlaceOrder(self, place_order_info):
    
        place_order_response = {}

        try:
            # Prepare the request headers
            headers = self.get_header()

            # Make the API call to place the order
            response = requests.post(self._rootUrl + self._routes['api.user.profile'], headers=headers, json=place_order_info)

            # Check the response status
            if response.status_code == 200:
                # Parse the JSON response
                place_order_response = response.json()
                self.uniqueorderid = place_order_info['uniqueorderid']
                
            else:
                # Log the error response
            
                place_order_response["status"] = "FAILED"
                place_order_response["message"] = response.text
                place_order_response["errorcode"] = response.status_code
                place_order_response["uniqueorderid"] = ""  # No unique order ID available on failure

        except Exception as e:
            

            place_order_response["status"] = "FAILED"
            place_order_response["message"] = str(e)
            place_order_response["errorcode"] = ""  
            place_order_response["uniqueorderid"] = "" 

        return place_order_response

    def ModifyOrder(self, modify_order_info):
  
        modify_order_response = {}

        try:
            # Prepare the request headers
            headers = self.get_header()

            # Make the API call to modify the order
            response = requests.post(self._rootUrl + "/rest/trans/v2/modifyorder", headers=headers, json=modify_order_info)

            # Check the response status
            if response.status_code == 200:
                # Parse the JSON response
                modify_order_response = response.json()
            
            else:
                
                modify_order_response["status"] = "FAILED"
                modify_order_response["message"] = response.text
                modify_order_response["errorcode"] = response.status_code

        except Exception as e:
        

            modify_order_response["status"] = "FAILED"
            modify_order_response["message"] = str(e)
            modify_order_response["errorcode"] = ""  

        return modify_order_response

    def CancelOrder(self,order_id, client_code=None):
  
        cancel_order_response = {}

        try:
            # Prepare the request headers
            headers =self.get_header()

            # Prepare the request data
            cancel_order_info = {
                "clientcode": client_code,  # Optional: only include if required
                "uniqueorderid": order_id   # Unique order ID to cancel
            }

            # Make the API call to cancel the order
            response = requests.post(self._rootUrl + "/rest/trans/v1/cancelorder", headers=headers, json=cancel_order_info)

            # Check the response status
            if response.status_code == 200:
                # Parse the JSON response
                cancel_order_response = response.json()
        
            else:
            
                cancel_order_response["status"] = "FAILED"
                cancel_order_response["message"] = response.text
                cancel_order_response["errorcode"] = response.status_code

        except Exception as e:
        

            cancel_order_response["status"] = "FAILED"
            cancel_order_response["message"] = str(e)
            cancel_order_response["errorcode"] = ""  

        return cancel_order_response


# Example usage:
client_id = "NAO791"  # Your client ID
password = "Sandeep@1"  # Your password
two_fa = "17/06/1973"  # Your 2FA
api_key = "V78Aq0o6V9I2ft4P"  # Your API key
# use code from ur authenticatior app 
totp = "670056"
# Instantiate the Oswal object
motilal_oswal = Oswal(api_key=api_key, client_code=client_id)

# Perform login
login_response = motilal_oswal.login(password, two_fa,totp)

if login_response.get("status") == "SUCCESS":
    auth_validation_response = motilal_oswal.validate_auth_token()
    a = motilal_oswal.GetProfile()
    print("a = ",a)

else:
    print("Login failed. Cannot validate AuthToken.")

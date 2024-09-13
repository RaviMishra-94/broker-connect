import pyotp
import os

def getTotp(totp_string: str) -> str:
    totp = pyotp.TOTP(totp_string)
    return totp.now()
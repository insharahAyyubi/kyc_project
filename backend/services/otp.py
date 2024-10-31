import requests
import random

def send_otp_via_textbelt(phone_number):
    otp = random.randint(100000, 999999)
    response = requests.post('https://textbelt.com/text', {
        'phone': phone_number,
        'message': f'Your OTP is {otp}',
        'key': '58386c8b9893691bb5ba487201a78566141a65b0pPBaYRbnnFy0BjA0aopHjNAWT',
    })
    result = response.json()
    print(result)
    return otp

# Usage
send_otp_via_textbelt('+919569879937')  # Replace with actual recipient phone number

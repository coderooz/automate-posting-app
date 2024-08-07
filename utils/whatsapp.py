import pywhatkit

def send_whatsapp_message(phone_number, message):
    pywhatkit.sendwhatmsg_instantly(phone_number, message)

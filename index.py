from flask import Flask, request
from twilio.twiml.voice_response import Gather, VoiceResponse, Say, Play
from twilio.rest import Client
import time
import json


app = Flask(__name__)

limited = False
numOfOpens = 0
password = 1010
isOpen = False

def reset_values():
    global isOpen
    global limited
    global numOfOpens
    limited = False
    numOfOpens = 0
    isOpen = False

def open_door(response):
    response.play(digits='w9')
    time.sleep(.3)
    return response

def send_confirmation(Confirmation):
    privateFile = open('./private.json')
    jsonKeys = json.load(privateFile)
    account_sid = jsonKeys["ActSid"]
    auth_token = jsonKeys["AuthKey"]
    userNumber = jsonKeys["UserNumber"]
    serverNumber = jsonKeys["MyNumber"]
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        to=userNumber,
        from_=serverNumber,
        body= Confirmation)
    privateFile.close()


@app.route("/voice", methods=['GET', 'POST'])
def voice():
    resp = VoiceResponse()
    print("HERE")
    print(str(resp))
    global isOpen
    global limited
    global numOfOpens
    global password
    if isOpen:
        resp.play(digits='wwwww9')
        time.sleep(2)
        print(str(resp))
        print(str(resp))
        return str(resp)
    if limited and numOfOpens > 0:
        numOfOpens -= 1
        if numOfOpens <= 0:
            limited = False
        open_door(resp)
        return str(resp)
    if password:
        gather = Gather(action='/gather')
        gather.say("Please Enter the password, then press pound")
        resp.append(gather)
        return str(resp)
    else:
        resp.say("Sorry, this apartment is not available right now")


@app.route('/gather', methods=['POST'])
def gather():
    resp = VoiceResponse()
    if 'Digits' in request.values:
        choice = request.values['Digits']
        if int(choice) == password:
            open_door(resp)
            return str(resp)
        else:
            resp.say("Invalid Password!")
            resp.hangup()
            return str(resp)


@app.route("/sms", methods=['POST'])
def incoming_sms():
    global isOpen
    global limited
    global numOfOpens
    global password
    body = request.values.get('Body', None)
    body = str(body)
    body = body.lower()
    words = body.split(" ")
    if "set" in words and "door" in words:
        if "open" in words:
            reset_values()
            isOpen = True
            send_confirmation("Door set to open")
            print(isOpen)
            return " "
        elif "closed" in words:
            reset_values()
            send_confirmation("Door set to closed")
            return " "
    if "set" in words and "password" in words:
        index = words.index("to")
        password = int(words[index + 1])
        send_confirmation("password changed to" + str(password))
        return " "

    if "limit" in words and "to" in words:
        index = words.index("to")
        reset_values()
        numOfOpens = int(words[index + 1])
        limited = True
        send_confirmation("Limit set to " + str(numOfOpens))
        return " "

    if "limit" in words and "off" in words:
        reset_values()
        send_confirmation("Limit is now off")
        return " "

    else:
        send_confirmation("Error parsing input")
        return " "



if __name__ == "__main__":
    app.run(debug=True)
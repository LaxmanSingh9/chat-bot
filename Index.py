from flask import Flask, request, render_template
import firebase_admin
from firebase_admin import credentials, db
import sys
# import os
# import uuid
# import base64
# import pyttsx3
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="keyfile.json"
# Open the log file in append mode
log_file = open('app.log', 'a')
sys.stdout = log_file

# Use a service account
cred = credentials.Certificate('./serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://polar-city-332413-default-rtdb.firebaseio.com'
})


app = Flask(__name__)


@app.route('/', methods=['GET'])
def webhook_1():
    return render_template('index.html')


@app.route('/webhook', methods=['POST'])
def webhook():
    # Log the received data
    data = request.get_json()
    try:
        user_context = data["queryResult"]["outputContexts"]
        for d in user_context:
          context_name = d["name"]
          if(context_name.find("session_data") != -1):
              data = d["parameters"]
              data_to_store = refine_data(data)
              ref = db.reference('webhook_data')
              ref.push(data_to_store)
              break
    except KeyError:
        print('Error while storing or getting the data')

    # Flush the log file
    log_file.flush()
    return  'OK', 200


def refine_data(user_data):
    print(f'data to be refine: {user_data}')
    refine_user_data = {
        "person_name": user_data.get("person.original", ""),
        "person_role": user_data.get("Role.original", ""),
        "restaurant_name": ", ".join(user_data.get("any.original", "")),
        "city": ", ".join(user_data.get("geo-city.original", "")),
        "street_address": ", ".join(user_data.get("street-address.original", "")),
        "cuisine_types": ", ".join(user_data.get("cuisine.original", "")),
        "resource_idle": user_data.get("ResourceIdleNess", ""),
        "other_apps": ", ".join(user_data.get("OtherApp.original", "")),
        "app_costing": user_data.get("unit-currency.original", ""),
        "equipments": ", ".join(user_data.get("Equipment.original", "")),
        "extra_capacity": user_data.get("CapacityType", "")
    }
    print(f'data to push: {refine_user_data}')
    return refine_user_data






if __name__ == '__main__':
    # Close the log file when the application exits
    try:
        app.run()
    finally:
        log_file.close()
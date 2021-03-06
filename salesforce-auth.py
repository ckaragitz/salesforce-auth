import jwt
import requests
import datetime
from simple_salesforce import Salesforce

# SFCC hardcoded config values
client_id = ""
client_secret = ""
sfcc_username = ""
sfcc_password=""
sfcc_token = ""

# dict to hold access token and expiration
access_token = {}
key_path = './private_key.pem'

with open(key_path) as pk:
    private_key = pk.read()

def sf_client():
    """ Leverage simple-salesforce library for bulk queries """

    return Salesforce(username=sfcc_username, password=sfcc_password, security_token=sfcc_token, domain='test')

def prep_request():
    """ Prepare the Salesforce API requests by fetching new access tokens and setting headers """
    
    #creds = jwt_login(client_id, sfcc_username, sandbox=True)
    creds = password_flow(sandbox=True)
    access_token = creds["access_token"]
    instance_url = creds["instance_url"]

    headers = {
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json",
        "Accept": "*/*"
    }

    return {"instance_url": instance_url, "headers": headers}

def jwt_login(client_id, username, sandbox=False):
    """ Sign a JWT and send to Salesforce in exchange for an access token """
    
    # get new token if first time or token has expired
    if not access_token or datetime.datetime.utcnow() > access_token.get('expiration'):
        pass
    else:
        return {"access_token": access_token.get("access_token"), "instance_url": access_token.get("instance_url")}

    endpoint = 'https://test.salesforce.com' if sandbox is True else 'https://login.salesforce.com'

    jwt_payload = jwt.encode(
        { 
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=30),
            'iss': client_id,
            'aud': endpoint,
            'sub': username
        },
        private_key,
        algorithm='RS256'
    )

    response = requests.post(
        endpoint + '/services/oauth2/token',
        data={
            'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
            'assertion': jwt_payload
        }
    )

    body = response.json()

    if response.status_code != 200:
        return {"error": body['error'], "message": body['error_description']}
    else:
        # set access token details
        access_token["access_token"] = body["access_token"]
        access_token["instance_url"] = body["instance_url"]
        access_token["expiration"] = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    
    return {"access_token": access_token.get("access_token"), "instance_url": access_token.get("instance_url")}

def password_flow(sandbox=False):

    # get new token if first time or token has expired
    if not access_token or datetime.datetime.utcnow() > access_token.get('expiration'):
        pass
    else:
        return {"access_token": access_token.get("access_token"), "instance_url": access_token.get("instance_url")}

    endpoint = 'https://test.salesforce.com' if sandbox is True else 'https://login.salesforce.com'

    params = {
        "grant_type": "password",
        "client_id": client_id,
        "client_secret": client_secret,
        "username": sfcc_username,
        "password": sfcc_password
        }
        
    response = requests.post(endpoint + "/services/oauth2/token", params=params)

    body = response.json()
    if response.status_code != 200:
        return {"error": body['error'], "message": body['error_description']}
    else:
        # set access token details
        access_token["access_token"] = body["access_token"]
        access_token["instance_url"] = body["instance_url"]
        access_token["expiration"] = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    
    return {"access_token": access_token.get("access_token"), "instance_url": access_token.get("instance_url")}

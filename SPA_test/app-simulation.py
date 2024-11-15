from flask import Flask, request, redirect, session, url_for, jsonify
import requests
import os
import argparse

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_azure_function_url(env):
    if env == "local":
        return os.getenv("LOCAL_AZURE_FUNCTION_URL")
    elif env == "azure":
        return os.getenv("AZURE_FUNCTION_URL")
    else:
        raise ValueError("Invalid environment. Use 'local' or 'azure'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set Azure Function URL based on environment.")
    parser.add_argument("env", choices=["local", "azure"], help="Environment to use (local or azure)")
    args = parser.parse_args()

    AZURE_FUNCTION_URL = get_azure_function_url(args.env)
    print(f"Using Azure Function URL: {AZURE_FUNCTION_URL}")

# Fetch environment variables directly (no need for dotenv)
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_CALLBACK_URL = os.getenv("AUTH0_CALLBACK_URL")

@app.route('/')
def home():
    print(f"home::Auth0 Domain: {AUTH0_DOMAIN}")
    print(f"home::Auth0 Audience: {AUTH0_AUDIENCE}")
    print(f"home::Auth0 Client ID: {AUTH0_CLIENT_ID}")
    print(f"home::Auth0 Callback URL: {AUTH0_CALLBACK_URL}")
    print(f"home::Azure Function URL: {AZURE_FUNCTION_URL}")
    return 'Welcome to the Auth0 example!'


# This route redirects to Auth0 for login
@app.route('/login')
def login():
    print(f"login::Login to Auth0")
    return redirect(f"https://{AUTH0_DOMAIN}/authorize?response_type=code&client_id={AUTH0_CLIENT_ID}&redirect_uri={AUTH0_CALLBACK_URL}&scope=openid profile email&audience={AUTH0_AUDIENCE}")



# This route is the callback URL for Auth0
@app.route('/callback')
def callback():
    print(f"callback::Callback from Auth0")
    code = request.args.get('code')
    if not code:
        return 'callback::Authorization code not found in the callback request.', 400

    token = exchange_code_for_token(code)
    if token:
        print(f"callback::Access Token: {token}")
        session['access_token'] = token
        print(f"callback::Bearer Token: {token}")
        return f'callback::Login successful! Bearer Token: {token}'
    else:
        print("Failed to obtain access token.")
        return 'callback::Failed to obtain access token.'



# This route is used to demonstrate the user profile retrieval from Auth0
@app.route('/user/profile/auth0')
def user_profile():
    print(f"user_profile::User Profile")
    access_token = session.get('access_token')
    if not access_token:
        return 'user_profile::Access token is missing. Please log in first.', 401

    url = f"https://{AUTH0_DOMAIN}/userinfo"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    print(f"user_profile::Access Token: {access_token}")

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print(f"user_profile::User Profile: {response.json()}")
        return jsonify(response.json())
    else:
        print(f"user_profile::Failed to fetch user profile: {response.status_code}")
        return f"user_profile::Failed to fetch user profile: {response.status_code}", response.status_code



# This route is used to demonstrate the user profile retrieval from Azure Function
@app.route('/user/profile', methods=['GET'])
def get_user():
    access_token = session.get('access_token')
    if not access_token:
        print("route::users::Access token is missing. Please log in first.")
        return 'route::users::Access token is missing. Please log in first.', 401

    # Compose the URL for the Azure Function
    url = f"{AZURE_FUNCTION_URL}/user/profile"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Request-ID": "12345"
    }

    # Debugging information
    print(f"route::users::Access Token: {access_token}")
    print(f"route::users::Azure Function URL: {url}")

    # Make a request to the Azure Function
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        print(f"route::users::Response Headers: {response.headers}")
        print(f"route::users::Response Content: {response.text}")
        return jsonify(response.json())
    except requests.exceptions.HTTPError as http_err:
        print(f"route::users::HTTP error occurred: {response.status_code} {http_err}")
        return f"route::users::HTTP error occurred: {response.status_code} {http_err}", response.status_code
    except requests.exceptions.RequestException as req_err:
        print(f"route::users::Request error occurred: {response.status_code} {req_err}")
        return f"route::users::Request error occurred: {response.status_code} {req_err}", response.status_code
    except ValueError as json_err:
        print(f"route::users::JSON decode error occurred: {json_err}")
        print(f"route::users::Response content: {response.text}")
        return f"route::users::JSON decode error occurred: {response.status_code} {json_err}", response.status_code
    except Exception as e:
        print(f"route::users::Unexpected error occurred: {response.status_code} {e}")
        return f"route::users::Unexpected error occurred: {response.status_code} {e}", response.status_code


# This route is used to demonstrate the user profile retrieval from Azure Function
@app.route('/patients', methods=['GET'])
def get_patients():
    access_token = session.get('access_token')
    if not access_token:
        print("route::patients::Access token is missing. Please log in first.")
        return 'route::patients::Access token is missing. Please log in first.', 401

    # Compose the URL for the Azure Function
    url = f"{AZURE_FUNCTION_URL}/patients"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Debugging information
    print(f"route::patients::Access Token: {access_token}")
    print(f"route::patients::Azure Function URL: {url}")

    # Make a request to the Azure Function
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        print(f"route::patients::Response Headers: {response.headers}")
        print(f"route::patients::Response Content: {response.text}")
        return jsonify(response.json())
    except requests.exceptions.HTTPError as http_err:
        print(f"route::patients::HTTP error occurred: {response.status_code} {http_err}")
        return f"route::patients::HTTP error occurred: {http_err}", response.status_code
    except requests.exceptions.RequestException as req_err:
        print(f"route::patients::Request error occurred: {response.status_code} {req_err}")
        return f"route::patients::Request error occurred: {req_err}", response.status_code
    except ValueError as json_err:
        print(f"route::patients::JSON decode error occurred: {json_err}")
        print(f"route::patients::Response content: {response.text}")
        print(f"route::patients::Response status code: {response.status_code}")
        return f"route::patients::JSON decode error occurred: {json_err}", response.status_code
    except Exception as e:
        print(f"route::patients::Unexpected error occurred: {response.status_code} {e}")
        return f"route::patients::Unexpected error occurred: {response.status_code} {e}", response.status_code



# New route to perform the curl request
@app.route('/update-user-profile', methods=['GET'])
def send_user_data():
    access_token = session.get('access_token')
    if not access_token:
        print("route::send-user-data::Access token is missing. Please log in first.")
        return 'route::send-user-data::Access token is missing. Please log in first.', 401

    url = f"{AZURE_FUNCTION_URL}/user/profile"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "name": "Peter Rock",
        "nickname": "perico",
        "family_name": "Rock",
        "given_name": "Peter",
        "picture": "https://rettx.eu/wp-content/uploads/2024/11/rettX-1.svg",
        "user_metadata": {
            "city": "Toledo",
            "country": "ES",
            "region": "Castilla-La Mancha"
            }
    }

    response = requests.patch(url, headers=headers, json=data)
    print(f"route::send-user-data::{response}")
    try:
        response.raise_for_status()
        print(f"route::send-user-data::Response Headers: {response.headers}")
        print(f"route::send-user-data::Response Content: {response.text}")
        return f"route::send-user-data::Successfully updated user profile: {response.text}", 200
    except requests.exceptions.HTTPError as http_err:
        print(f"route::send-user-data::HTTP error occurred: {http_err}")
        return f"route::send-user-data::HTTP error {response.status_code} {response.text}", response.status_code
    except requests.exceptions.RequestException as req_err:
        print(f"route::send-user-data::Request error occurred: {req_err}")
        return f"route::send-user-data::Request error occurred: {response.status_code} {response}", response.status_code
    except ValueError as json_err:
        print(f"route::send-user-data::JSON decode error occurred: {json_err}")
        print(f"route::send-user-data::Response content: {response.text}")
        print(f"route::send-user-data::Response status code: {response.status_code}")
        return f"route::send-user-data::JSON decode error occurred: {response.status_code} {json_err}", response.status_code
    except Exception as e:
        print(f"route::send-user-data::Unexpected error occurred: {e}")
        return f"route::send-user-data::Unexpected error occurred: {response.status_code} {e}", response.status_code



# This function exchanges the authorization code for an access token
def exchange_code_for_token(auth_code):
    url = f"https://{AUTH0_DOMAIN}/oauth/token"
    headers = {'content-type': 'application/json'}
    payload = {
        'grant_type': 'authorization_code',
        'client_id': AUTH0_CLIENT_ID,
        'client_secret': AUTH0_CLIENT_SECRET,
        'code': auth_code,
        'redirect_uri': AUTH0_CALLBACK_URL
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"exchange_code_for_token::Access Token: {response.json().get('access_token')}")
        return response.json().get('access_token')
    else:
        print(f"exchange_code_for_token::Failed to obtain access token: {response.status_code} {response.text}")
        return None



if __name__ == '__main__':
    app.run(debug=True, port=3000)
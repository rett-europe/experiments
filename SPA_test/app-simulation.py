from flask import Flask, request, redirect, session, url_for, jsonify, render_template_string
import requests
import os
import argparse
from azure.storage.blob import BlobClient

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

    # Check for error in query parameters
    error = request.args.get('error')
    error_description = request.args.get('error_description')
    
    if error:
        # Log the error details for debugging
        print(f"callback::Error: {error}, Description: {error_description}")
        return f"Error: {error}. {error_description}", 400

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

    access_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IldOVy1KcGJpejBXYXRUMHBuU0NSNCJ9.eyJpc3MiOiJodHRwczovL2xvZ2luLnJldHR4LmV1LyIsInN1YiI6ImF1dGgwfDY3NDg5MGY3OTQ5YzI4NGZjNTlhYjIwOSIsImF1ZCI6WyJodHRwczovL3JldHQtZXVyb3BlLmV1LmF1dGgwLmNvbS9hcGkvdjIvIiwiaHR0cHM6Ly9yZXR0LWV1cm9wZS5ldS5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNzMyODczMjYyLCJleHAiOjE3MzI5NTk2NjIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJhenAiOiJVbXpkZzgybXhOcTV0RnVOSFpFblo3Tzg3aDc3anJhNyJ9.DFAN-h4krplJh91XhfBoO-Vj01f6a4j3N6kevUx6qjaah1VjwDimH-WRwh2qudBTGtzq_XcIH63RucnEOk1DbVYqBtJOtE0Xsa__7KiA8gK-Zhk1twlURQ-usbxTuVThkTP1qpFshKoBSoRkSnPkEet9YWNQN0RozKxQR4Y6st46VUrwcmVBaGEp1pQDxhU_UuOkWgIyYuerRnEZqy1iT61Ilfp2Q13K0qL4r0kDjEpOh7Md4uX60KHg2WrvUIZsg1Us1PekwnEklPLTgHDlQCEMXP7yff5zC_qWPzOXoaPKcE4rXnnBiZouxYQ8B-WrlKkmLmplWTOhtkClQeK2Wg"
    id_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IldOVy1KcGJpejBXYXRUMHBuU0NSNCJ9.eyJuaWNrbmFtZSI6InRvbSIsIm5hbWUiOiJ0b21AcmV0dHguZXUiLCJwaWN0dXJlIjoiaHR0cHM6Ly9zLmdyYXZhdGFyLmNvbS9hdmF0YXIvYmNiZTIxY2QyN2FlNTBmZjBmYWEyMGY1YzI0YTQ5NTk_cz00ODAmcj1wZyZkPWh0dHBzJTNBJTJGJTJGY2RuLmF1dGgwLmNvbSUyRmF2YXRhcnMlMkZ0by5wbmciLCJ1cGRhdGVkX2F0IjoiMjAyNC0xMS0yOFQxNTo1NTo0Ny40OTZaIiwiZW1haWwiOiJ0b21AcmV0dHguZXUiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6Ly9sb2dpbi5yZXR0eC5ldS8iLCJhdWQiOiJVbXpkZzgybXhOcTV0RnVOSFpFblo3Tzg3aDc3anJhNyIsImlhdCI6MTczMjg3MzI2MiwiZXhwIjoxNzMyOTA5MjYyLCJzdWIiOiJhdXRoMHw2NzQ4OTBmNzk0OWMyODRmYzU5YWIyMDkiLCJzaWQiOiI0VWN0czc4S3Q3REFZUWRwdmZnY2NpdVBfeDd5MUlfYiJ9.eayzkhTomLzXutWmJDjPRnSD91PoLSYpBIAjfjUJ5yxqTCzZrVBEL_6HfpxYkiD3FiTAe5mKUwwyxigft7CUQ4X9jNQ2bkkjsTg9_z6b-ReHemJl91IDwv4GUMnixqa0ZyQdKUgpD11yH6-JyLRfgkuPKEHVe9n75nd-Q11nVjWeN_GD6SRRuveVcZUsDEkMuv03o98omEUCZC0uA9uNp9uFf0sM-G77o0QiTGqXTpbtFfPIWUwobqI-5MQ7pRj4Hfktsl4f1eCe-bGh7um89FO9olkRHHb1qVrF5pm4FSMqgFkxLKOv1LmxxAChjBTGogviIhw1wLxg1ehu07tOwg"

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



@app.route('/get-upload-url', methods=['GET', 'POST'])
def get_upload_url():
    access_token = session.get('access_token')
    if not access_token:
        return 'Access token is missing. Please log in first.', 401

    if request.method == 'POST':
        # Collect form inputs
        patient_id = request.form.get('patient_id')
        file_name = request.form.get('file_name')
        file_type = request.form.get('file_type')

        if not patient_id or not file_name or not file_type:
            return "All fields (patient_id, file_name, file_type) are required.", 400

        # Construct the URL and parameters according to the endpoint’s requirements
        # Assuming the endpoint is something like:
        # POST /patients/{id}/files/upload-file-info?file_name=xxx&file_type=yyy

        upload_info_url = f"{AZURE_FUNCTION_URL}/patients/{patient_id}/files/upload-file-info"
        params = {
            "file_name": file_name,
            "file_type": file_type
        }

        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        # Make the POST request
        response = requests.post(upload_info_url, headers=headers, params=params)
        if response.status_code != 200:
            return f"Failed to get upload info: {response.status_code} {response.text}", response.status_code

        upload_info = response.json()
        file_url = upload_info.get('file_url')
        if not file_url:
            return "No file_url returned in upload info.", 500

        # Store the URL in the session or just display it
        session['upload_file_url'] = file_url

        # Display the result
        return f"""
        <h2>Upload URL Retrieved</h2>
        <p>Expiration: {upload_info.get('expiration')}</p>
        <p>File ID: {upload_info.get('file_id')}</p>
        <p>Patient ID: {upload_info.get('patient_id')}</p>
        <p>Full URL: <a href="{file_url}" target="_blank">{file_url}</a></p>
        <p><a href="/upload-file" target="_blank">Click here to upload the file now</a></p>
        """

    # If GET request, show the form
    return render_template_string('''
    <!doctype html>
    <html>
    <head><title>Get Upload URL</title></head>
    <body>
      <h1>Get Upload URL for Patient File</h1>
      <form method="post">
        <label for="patient_id">Patient ID:</label><br>
        <input type="text" id="patient_id" name="patient_id" required><br><br>

        <label for="file_name">File Name (e.g. "GeneticReport5_en.pdf"):</label><br>
        <input type="text" id="file_name" name="file_name" required><br><br>

        <label for="file_type">File Type (e.g. "genetic-report"):</label><br>
        <input type="text" id="file_type" name="file_type" required><br><br>

        <input type="submit" value="Get Upload URL">
      </form>
    </body>
    </html>
    ''')


from azure.storage.blob import BlobClient, ContentSettings
from flask import request

@app.route('/upload-file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part in the request.", 400

        file = request.files['file']
        if file.filename == '':
            return "No selected file.", 400

        blob_url = session.get('upload_file_url')
        if not blob_url:
            return "No upload URL available. Please retrieve one first via /get-upload-url.", 400

        blob_client = BlobClient.from_blob_url(blob_url)
        content_settings = ContentSettings(content_type=file.content_type)

        blob_client.upload_blob(file, blob_type="BlockBlob", content_settings=content_settings, overwrite=True)
        return "File uploaded successfully!", 200

    # If GET request, show the form
    return render_template_string('''
    <!doctype html>
    <html>
    <head><title>Upload File</title></head>
    <body>
      <h1>Upload File</h1>
      <form method="post" enctype="multipart/form-data">
        <label for="file">Choose file to upload:</label><br>
        <input type="file" id="file" name="file" required><br><br>
        <input type="submit" value="Upload File">
      </form>
    </body>
    </html>
    ''')




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
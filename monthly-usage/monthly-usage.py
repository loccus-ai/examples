import requests
import datetime
import isodate
import math


# User Defined Variables
USERNAME = ""
PASSWORD = ""
ORG = ""

# Define the endpoint URLs
login_url = "https://api.loccus.ai/v1/auth/credentials"
org_records_url = f"https://api.loccus.ai/v1/orgs/{ORG}/records/verification"

#################################################################
#### LOGIN
#################################################################
print("🔒 Logging in...")

# Make the POST request with the payload
response = requests.post(login_url, json={"handle": USERNAME, "password": PASSWORD})

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Get the JSON response from the request
    json_response = response.json()
    token = json_response["token"]
else:
    print("Failed to login. Status code:", response.status_code)
    print(response)
    exit(1)

# Define the headers with Authorization header
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
print("🔓 Log in successful!")

#################################################################
#### GET VERIFICATION RECORDS
#################################################################


current_year = datetime.datetime.now().year
current_month = datetime.datetime.now().month

month_start = f"{current_year}-{current_month:02}-01T00:00:00.000000Z"

page = 1
total_seconds = 0
print("🧮 Getting the verification records...")
while True:
    records_response = requests.get(org_records_url, headers=headers, params={"page": page, "after": month_start})


    if records_response.status_code != 200:
        print("Failed to fetch the verification usage records. Status code:", records_response.status_code)
        print(records_response)
        exit(1)

    # Get the JSON response from the request
    records_json = records_response.json()

    if len(records_json) == 0:
        break
    
    print(f"📄 Checking the page {page}...")
    page += 1

    for record in records_json:
        space = record["space"]["handle"]
        verification = record["verification"]["handle"]
        verification_type = record["verification"]["type"]

        #print(f"Looking up verification {verification} in space {space}")

        verification_url = f"https://api.loccus.ai/v1/spaces/{ORG}/{space}/verifications/{verification_type}/{verification}"
        verification_response = requests.get(verification_url, headers=headers)

        if verification_response.status_code != 200:
            print("Failed to fetch the verification. Status code:", verification_response.status_code)
            print(verification_response)
            exit(1)

        verification_json = verification_response.json()
        audio = verification_json["audio"]["handle"]

        audio_url = f"https://api.loccus.ai/v1/spaces/{ORG}/{space}/audios/{audio}"
        audio_response = requests.get(audio_url, headers=headers)

        if audio_response.status_code != 200:
            print("Failed to fetch the audio. Status code:", audio_response.status_code)
            print(audio_response)
            exit(1)

        audio_json = audio_response.json()
        duration = audio_json["duration"]
        duration_seconds = isodate.parse_duration(duration).total_seconds()
        total_seconds += duration_seconds


print("\n")
print(f"#############################################################")
print(f"Total verification usage for this month (since {month_start:10}) for the org {ORG}: {math.ceil(total_seconds/60)} minutes")


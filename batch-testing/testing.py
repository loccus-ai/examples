import requests
import os
import base64
from tabulate import tabulate


# User Defined Variables - Loaded from Environment Variables
USERNAME = os.getenv("HIYA_USERNAME")
PASSWORD = os.getenv("HIYA_PASSWORD")
SPACE = os.getenv("HIYA_SPACE", "demo")
THRESHOLD = float(os.getenv("HIYA_THRESHOLD", "0.5"))

# Check if mandatory environment variables are set
if not all([USERNAME, PASSWORD]):
    missing_vars = []
    if not USERNAME:
        missing_vars.append("HIYA_USERNAME")
    if not PASSWORD:
        missing_vars.append("HIYA_PASSWORD")
    print(f"Error: The following environment variables are not set: {', '.join(missing_vars)}")
    print("Please set them before running the script.")
    exit(1)

# Path to the "audios" folder
folder_path = "audios"

# Define the endpoint URLs
region = "eu"
domain = "api.hiya.com"
login_url = f"https://{domain}/audiointel/{region}/v1/auth/credentials"
audio_create_url = f"https://{domain}/audiointel/{region}/v1/spaces/{USERNAME}/{SPACE}/audios"
verification_create_url = f"https://{domain}/audiointel/{region}/v1/spaces/{USERNAME}/{SPACE}/verifications/authenticity"


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
#### UPLOAD AUDIOS & VERIFY
#################################################################
print(f"⚙️  Uploading and verifying the audios inside {folder_path}...")

# Counters
synthetic_list = []
not_enough_voice_list = []
valid_list = []
partial_spoof_dict = {}

# Iterating over all audios in the folder
for file_name in os.listdir(folder_path):
    # Checking if the path is a file (not a folder)
    if not os.path.isfile(os.path.join(folder_path, file_name)):
        continue

    print(f"\t ⏳Processing {file_name}...\r", end="")
    # Read the binary content of the file as bytes
    with open(os.path.join(folder_path, file_name), "rb") as file:
        binary_content = file.read()

    # Encode the binary content to base64
    base64_content = base64.b64encode(binary_content).decode("utf-8")

    response = requests.post(
        audio_create_url, headers=headers, json={"file": base64_content}
    )

    # Check if the request wasn't successful
    if response.status_code >= 400:
        print(f"Failed to upload file {file_name}. Status code:", response.status_code)
        print(response)
        exit(1)

    audio_handle = response.json()["handle"]
    audio_sample_rate = response.json()["sampleRate"]

    # We select the model based on the sample_rate
    if int(audio_sample_rate) < 16000:
        model = "phone"
    else:
        model = "digital"

    response = requests.post(
        verification_create_url,
        headers=headers,
        json={"model": model, "audio": audio_handle},
    )

    partial_spoof_dict[file_name] = response.json().get("partialSpoof", "False")

    if response.json()["scores"]["synthesis"] == None:
        not_enough_voice_list.append((file_name, audio_voice_duration))
    else:
        synthesis_score = float(response.json()["scores"]["synthesis"])

        if synthesis_score < THRESHOLD:
            synthetic_list.append((file_name, synthesis_score))
        else:
            valid_list.append((file_name, synthesis_score))


print("\n")
print("\n")
print("Voice Verification Batch Finished")
print(f"\t ✅ {len(valid_list)} Audios are authentic")
print(
    f"\t 🤐 {len(not_enough_voice_list)} Audios don't have enough voice for the verification"
)
print(f"\t 🤖 {len(synthetic_list)} Audios are detected as synthetic")

print("\n")
print(f"#############################################################")
print(f"📋✅ List of Authentic Audios")
print(f"#############################################################")
print(
    tabulate(
        [("Audio", "Synthetic Score")] + valid_list,
        headers="firstrow",
        tablefmt="fancy_grid",
    )
)

print("\n")
print(f"#############################################################")
print(f"📋🤐 List of Audios which don't have enough voice for the verification")
print(f"#############################################################")
print(
    tabulate(
        [("Audio", "Voice Duration")] + not_enough_voice_list,
        headers="firstrow",
        tablefmt="fancy_grid",
    )
)

print("\n")
print(f"#############################################################")
print(f"📋🤖 List of Audios are detected as synthetic")
print(f"#############################################################")
print(
    tabulate(
        [("Audio", "Synthesis Score")] + synthetic_list,
        headers="firstrow",
        tablefmt="fancy_grid",
    )
)

print("\n")
print(f"#############################################################")
print(f"Partial Spoof Results")
print(f"#############################################################")
print(
    tabulate(
        [("Audio", "Partial Spoof Result")] + [item for item in partial_spoof_dict.items()],
        headers="firstrow",
        tablefmt="fancy_grid",
    )
)
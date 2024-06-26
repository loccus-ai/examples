import requests
import os
import base64
from tabulate import tabulate


# User Defined Variables
USERNAME = ""
PASSWORD = ""
SPACE = ""
THRESHOLD = 0.5

# Path to the "audios" folder
folder_path = "audios"

# Define the endpoint URLs
login_url = "https://api.loccus.ai/v1/auth/credentials"
audio_create_url = f"https://api.loccus.ai/v1/spaces/{USERNAME}/{SPACE}/audios"
verification_create_url = f"https://api.loccus.ai/v1/spaces/{USERNAME}/{SPACE}/verifications/authenticity"


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
replay_list = []
synthetic_list = []
replay_and_synthetic_list = []
not_enough_voice_list = []
valid_list = []

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
    audio_voice_duration = response.json()["voiceDuration"]
    audio_sample_rate = response.json()["sampleRate"]

    # We select the model based on the sample_rate
    if int(audio_sample_rate) < 16000:
        model = "telephone"
    else:
        model = "default"

    response = requests.post(
        verification_create_url,
        headers=headers,
        json={"model": model, "audio": audio_handle},
    )

    if response.status_code >= 400:
        not_enough_voice_list.append((file_name, audio_voice_duration))
    else:
        score = float(response.json()["score"])
        replay_score = float(response.json()["subscores"]["replay"])
        synthesis_score = float(response.json()["subscores"]["synthesis"])

        if replay_score < THRESHOLD and synthesis_score < THRESHOLD:
            replay_and_synthetic_list.append((file_name, replay_score, synthesis_score))
        elif replay_score < THRESHOLD:
            replay_list.append((file_name, replay_score, synthesis_score))
        elif synthesis_score < THRESHOLD:
            synthetic_list.append((file_name, replay_score, synthesis_score))
        else:
            valid_list.append((file_name, replay_score, synthesis_score))


print("\n")
print("\n")
print("Voice Verification Batch Finished")
print(f"\t ✅ {len(valid_list)} Audios are authentic")
print(
    f"\t 🤐 {len(not_enough_voice_list)} Audios don't have enough voice for the verification"
)
print(f"\t 🔊 {len(replay_list)} Audios are detected as replayed")
print(f"\t 🤖 {len(synthetic_list)} Audios are detected as synthetic")
print(
    f"\t 🤖🔊 {len(replay_and_synthetic_list)} Audios are detected as replayed and synthetic"
)

print("\n")
print(f"#############################################################")
print(f"📋✅ List of Authentic Audios")
print(f"#############################################################")
print(
    tabulate(
        [("Audio", "Replay Score", "Synthetic Score")] + valid_list,
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
print(f"📋🔊 List of Audios that are detected as replayed")
print(f"#############################################################")
print(
    tabulate(
        [("Audio", "Replay Score", "Synthetic Score")] + replay_list,
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
        [("Audio", "Replay Score", "Synthetic Score")] + synthetic_list,
        headers="firstrow",
        tablefmt="fancy_grid",
    )
)


print("\n")
print(f"#############################################################")
print(f"📋🤖🔊 List of Audios are detected as replayed and synthetic")
print(f"#############################################################")
print(
    tabulate(
        [("Audio", "Replay Score", "Synthetic Score")] + replay_and_synthetic_list,
        headers="firstrow",
        tablefmt="fancy_grid",
    )
)

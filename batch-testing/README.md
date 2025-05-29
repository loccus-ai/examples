# Batch Audio Authenticity Testing Example
In this example we do a batch verification of all the audios inside the `/audios/` folder. This is meant to facilitate the Hiya API Usage.

# Prerequisites
1. You need a Hiya account. [You can register here](https://developer.hiya.com/console/audiointel/signup)
2. You need to install python. [You can download python here](https://www.python.org/downloads/)
3. You need to install the python dependencies:
    ```sh
    pip3 install requests tabulate
    ```

# Execute the batch testing
## 1. Load the audios
You must place the audios that you want to verify inside the `/audios/` folder. [You can check here the audio requirements](https://docs.loccus.ai/api-reference/audios/requirements).

## 2. Set the required environment variables.
Before running the script, you need to set the following environment variables. You can do this in your terminal session or by adding them to your shell's configuration file (e.g., `.bashrc`, `.zshrc`).

```sh
export HIYA_USERNAME="<YOUR_USERNAME>"
export HIYA_PASSWORD="<YOUR_PASSWORD>"
# Optional: Set a custom threshold (defaults to 0.5 if not set)
# export HIYA_THRESHOLD="0.6"
```
Replace `<YOUR_USERNAME>`, `<YOUR_PASSWORD>` with your actual Hiya credentials.

## 3. Execute the test script
Once the environment variables are set, you can run the script:
```sh
python3 testing.py
```

## 4. Review the results
The testing script will print an overview of the audio verification to the console.

Additionally, a `results.csv` file will be generated in the same directory. This file contains a detailed breakdown for each processed audio, including:
- **Audio Filename**: The name of the audio file.
- **Synthesis Score**: The synthesis score from the verification (or "N/A" if not applicable).
- **Partial Spoof**: The partial spoof detection result (e.g., "True" or "False").
- **Classification**: The overall classification of the audio (e.g., "Synthetic", "Authentic", "Not Enough Voice").

If you want to get more details or manage your audios and verifications, you can also view the results in the [Hiya Console](https://developer.hiya.com/console/audiointel/signin).

# Batch Audio Authenticity Testing Example
We will do a batch verification of all the audios inside the `/audios/` folder.

# Prerequisites
1. You need a Loccus AI account. [You can register here](https://demo.loccus.ai/signup)
2. You need an space inside Loccus AI Platform. For creating the space, please contact support@loccus.ai
2. You need to install python. [You can download python here](https://www.python.org/downloads/)
3. You need to install the python dependencies:
    ```sh
    pip3 install requests tabulate
    ```

# Execute the batch testing
## 1. Load the audios
You must place the audios that you want to verify inside the `/audios/` folder. [You can check here the audio requirements](https://docs.loccus.ai/api-reference/audios/requirements).

## 2. Set the requiered variables inside the script file.
You must specify your Loccus AI username, password and space inside `testing.py`: 
```text
USERNAME = "<YOUR USERNAME>"
PASSWORD = "<YOUR PASSWORD>"
SPACE = "<YOUR SPACE>"
```

## 3. Execute the test script
```sh
python3 testing.py
```

## 4. Review the results
The testing script will print the overview of the audios verification. If you want to get more details, you can view the verification results in the [Loccus AI Console](https://console.loccus.ai/).

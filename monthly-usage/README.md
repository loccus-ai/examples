# Org Monthly Usage Example
In this example we check all the verifications performed inside an organization, in order to calculate the minutes of audio verified.

# Prerequisites
1. You need a Loccus AI account. [You can register here](https://demo.loccus.ai/signup)
2. You need to install python. [You can download python here](https://www.python.org/downloads/)
3. You need to install the python dependencies:
    ```sh
    pip3 install requests isodate
    ```

# Execute the batch testing
## 1. Set the requiered variables inside the script file.
You must specify your Loccus AI username, password and organization inside `monthly-usage.py`: 
```text
USERNAME = "<YOUR USERNAME>"
PASSWORD = "<YOUR PASSWORD>"
ORG = "<YOUR ORGANIZATION>"
```

The script will output the monthly usage of the API inside the organization, in minutes.

## 3. Execute the test script
```sh
python3 monthly-usage.py
```

## 4. Review the results
The script will print the total minutes of audio verified by the organization in the current month.

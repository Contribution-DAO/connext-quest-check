# Connext Quest Checker
This repository was used to automate check on the Connext quest. For the criteria, see `conf` for more details

## Requirments
- We use Python 3.10.8 for development, but Python 3.8+ could also works just fine
- Make sure you have Twitter API that have access to V2 API

## Setup
Put your twitter's Bearer token into `.env` file. See `.env.example` on how to add one.

## Usage

### (Recommended) Create your virtualenv
```bash
python3 -m venv quest.venv
source quest.venv/bin/activate
```

### Install requirements
```bash
pip3 install -r requirements.txt
```

### Add user list to check
In `conf/quest_week1.yaml`, make sure you configure `users_path`, and `export_path`. The `users_path` should contains the path to the text file with the following format

```
<twitter-username1>
<twitter-username2>
<twitter-username3>
...
```

### Run the script
```bash
python3 main.py
```

### Check the result
The exported results were a JSON file saved in the path specified in `export_path` in config file.

## Author
`chompk.eth | Contribution DAO#9502`
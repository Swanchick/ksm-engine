# Instance 
`https://<domain_name>/api/instance/`

---
## /api/instance/start_server/
### Method type `POST`
### Required data
* Engine password: `str`
* User key: `str`
* instance_id: `int`
### Response data
* status `int`
* message `str`
### Example
```py
import requests

url = "/api/instance/start_server/"

headers = {
    "Content-Type": "application/json"
}

data = {
    "password": "<engine_password>",
    "user_key": "<user_key>",
    "instance_data": {
        "instance_id": <instance_id>
    }
}

response = requests.post(url, headers=headers, json=data)
```
---

## /api/instance/stop_server/
### Method type `POST`
### Required data
* Engine password: `str`
* User key: `str`
* instance_id: `int`
### Response data
* status `int`
* message `str`
### Example
```py
import requests

url = "/api/instance/stop_server/"

headers = {
    "Content-Type": "application/json"
}

data = {
    "password": "<engine_password>",
    "user_key": "<user_key>",
    "instance_data": {
        "instance_id": <instance_id>
    }
}

response = requests.post(url, headers=headers, json=data)
```
---

## /api/instance/server_send/
### Method type `POST`
### Required data
* Engine password: `str`
* User key: `str`
* instance_id: `int`
* args: `List[str]`
### Response data
* status `int`
* message `str`
### Example
```py
import requests

url = "/api/instance/server_send/"

headers = {
    "Content-Type": "application/json"
}

data = {
    "password": "<engine_password>",
    "user_key": "<user_key>",
    "instance_data": {
        "instance_id": <instance_id>,
        "args": [
            "<commands>"
        ]
    }
}

response = requests.post(url, headers=headers, json=data)
```
---

## /api/instance/get_output/
### Method type `POST`
### Required data
* Engine password: `str`
* User key: `str`
* instance_id: `int`
### Response data
* status `int`
* message `str`
* outputs `List[str]`
### Example
```py
import requests

url = "/api/instance/server_send/"

headers = {
    "Content-Type": "application/json"
}

data = {
    "password": "<engine_password>",
    "user_key": "<user_key>",
    "instance_data": {
        "instance_id": <instance_id>
    }
}

response = requests.post(url, headers=headers, json=data)
```
---

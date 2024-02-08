import requests
import urllib3
import json
from pathlib import Path
from requests.auth import HTTPBasicAuth
import csv


def get_vm_uuids(creds):
    PE_IP = creds[0]
    user=creds[1]
    passw=creds[2]
    headers = {"Content-Type": "application/json", "charset": "utf-8"}
    endpoint  = "https://{}:9440/PrismGateway/services/rest/v2.0/vms/".format(PE_IP)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    response = requests.get(endpoint,auth=(user, passw),headers=headers,verify=False)
    vms_uuid = []
    for obj in response.json()["entities"]:
        vms_uuid.append([obj['name'],obj['uuid']])
    #print(vms_uuid)
    with open("generated_vms_uuid.json","w") as json_file:
         json.dump(vms_uuid,json_file,indent=4)
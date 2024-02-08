import requests
import urllib3
import json
from pathlib import Path
from requests.auth import HTTPBasicAuth
import csv


#this script has GUI 

def take_snapshots(creds,uuid):
    PC_IP = creds[0]
    user=creds[1]
    passw=creds[2]
    print(creds)
    headers = {"Content-Type": "application/json", "charset": "utf-8"}
    endpoint = "https://{}:9440/api/nutanix/v3/vms/{}/snapshot".format(PC_IP,uuid)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    body = { "name":"MANUAL_RP"
    }
    response = requests.post(endpoint,auth=(user, passw),headers=headers,verify=False,data=json.dumps(body))
    #print(response.json())
    return response


def get_vm_uuidsc(creds):
    PC_IP = creds[0]
    user=creds[1]
    passw=creds[2]
    headers = {"Content-Type": "application/json", "charset": "utf-8"}
    endpoint = "https://{}:9440/api/nutanix/v3/vms/list".format(PC_IP)
    print(creds)
    #endpoint  = "https://{}:9440/PrismGateway/services/rest/v2.0/vms/".format(PE_IP)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    body = {"kind":"vm","length":500}
    try:
        response = requests.post(endpoint,auth=(user, passw),headers=headers,verify=False,data=json.dumps(body))
        if response.status_code != 200:
            return None
    except TimeoutError:
        return None
    print(response.status_code)
    vms_uuid = []
    vm_count = 0
    #print(list(response.json()))
    #print(list(response.json()["metadata"]))
    #return
    for obj in response.json()["entities"]:
        item = {}
        item["vm_name"] = obj["status"]["name"]
        item["uuid"] = obj["metadata"]["uuid"]
        vms_uuid.append(item)
        vm_count+=1
    obj = {}
    obj["Vm_count"] = vm_count
    vms_uuid.append(obj)
        #vms_uuid.append(item)
    #print(vms_uuid)
    with open("pc_generated_vms_uuid.json","w") as json_file:
         json.dump(vms_uuid,json_file,indent=4)
    return []

#creds = ["10.38.87.39","admin","nx2Tech737!"]
#get_vm_uuidsc(creds)
#take_snapshots(creds)
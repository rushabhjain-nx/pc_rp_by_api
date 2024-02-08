import requests
import urllib3
import json
from pathlib import Path
from requests.auth import HTTPBasicAuth
import csv

#https://10.38.87.39:9440/api/nutanix/v3/vms/971c419a-72c8-494c-83f6-81423b0f2048/snapshot

#this script does not have GUI

def take_snapshots(creds):

    PC_IP = creds[0]
    user=creds[1]
    passw=creds[2]
    body = {}
   # endpoint = "https://{}/api/nutanix/v3/vms/{}/snapshot".format()
    with open('data.csv', mode='r') as file:
        reader = csv.reader(file)
    # Iterate over each row in the CSV
        for row in reader:
        # Each row is a list of values
            print("current uuid :",row[0])
            endpoint = "https://{}:9440/api/nutanix/v3/vms/{}/snapshot".format(PC_IP,row[0])
            headers = {"Content-Type": "application/json", "charset": "utf-8"}
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = requests.post(endpoint,auth=(user, passw),headers=headers,verify=False,data=json.dumps(body))
            print(response.json())
   


def get_vm_uuids(creds):
    PC_IP = creds[0]
    user=creds[1]
    passw=creds[2]
    headers = {"Content-Type": "application/json", "charset": "utf-8"}
    endpoint = "https://{}:9440/api/nutanix/v3/vms/list".format(PC_IP)

   
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    body = {"kind":"vm","length":500}
    try:
        response = requests.post(endpoint,auth=(user, passw),headers=headers,verify=False,data=json.dumps(body))
    except TimeoutError:
        print("Connection Timed Out!")
        return None
    
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
    with open("pc_generated_vms_uuid.json","w") as json_file:
         json.dump(vms_uuid,json_file,indent=4)

    return []

creds = ["10.32.87.39","admin","nx2Tech737!"]


get_vm_uuids(creds)
#take_snapshots(creds)
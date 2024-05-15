import requests
import urllib3
import json
from pathlib import Path
from requests.auth import HTTPBasicAuth
import csv
from datetime import datetime


def get_vms_form_pe():
    with open("prism_element_creds.json", 'r') as file:
    # Load the JSON data
        pe_creds_data = json.load(file)
    print(pe_creds_data)

    data=[]
    headers = {"Content-Type": "application/json", "charset": "utf-8"}
    count = 0
    for pe in pe_creds_data:
        Pe_IP = pe["ip"]
        user=pe["username"]
        passw=pe["password"]
        endpoint = "https://{}:9440/PrismGateway/services/rest/v2.0/vms/".format(Pe_IP)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(endpoint,auth=(user, passw),headers=headers,verify=False)
        #print(response.status_code)
        if response.status_code != 200:
            print("Error is getting VMS for PE : ",Pe_IP)
            return None
    #print(response.json())


        for obj in response.json()["entities"]:
            item = {}
            item["vm_name"] = obj["name"]
            item["uuid"] = obj["uuid"]
            item["cip"] = Pe_IP
            data.append(item)
            count+=1
        #print(item)

    print("TOTAL VMS FETCHED  : ", count)

    data = sorted(data, key=lambda x: x.get('cip', ''))

    with open("vms_from_pe.json","w") as json_file:
         print("VMs fetched from PE and saved in vms_from_pe.json")
         json.dump(data,json_file,indent=4)

    return 1

#this script has GUI 
def get_pe(creds):
    PC_IP = creds[0]
    user=creds[1]
    passw=creds[2]
    headers = {"Content-Type": "application/json", "charset": "utf-8"}
    endpoint = "https://{}:9440/api/nutanix/v3/groups".format(PC_IP)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    body = { "entity_type":"cluster","group_member_attributes":
            [{"attribute":"name"},{"attribute":"version"},{"attribute":"is_available"},
             {"attribute":"service_list"},{"attribute":"full_version"},
             {"attribute":"external_ip_address"}]
    }
    response = requests.post(endpoint,auth=(user, passw),headers=headers,verify=False,data=json.dumps(body))
    if response.status_code != 200:
        return None
    #print(list(response.json()))
    print()
   # print(list(response.json()["group_results"][0]["entity_results"][0]['data']))
    data = []
    n = int(response.json()["total_entity_count"])
    #print(n)
    uuid=""
    c=0
    for i in range(n):
       # print(list(response.json()["group_results"][0]["entity_results"]))
        uuid = response.json()["group_results"][0]["entity_results"][i]["entity_id"]
        obj = response.json()["group_results"][0]["entity_results"][i]["data"]
        name=""
        ip=""
        
        for item in obj:
            #print(item)
            if item['name']=='name':
                name = item['values'][0]['values'][0]
                #print(name)
            if item['name']=='external_ip_address':
                ip = item['values'][0]['values'][0]
                #print(ip)
        c=c+1
        data.append({"index":c,"uuid":uuid,"name":name,"ip":ip})

    #print(data)
    with open("pe_list_generated.json","w") as json_file:
         print("Prism element data fetched from PC and saved in pe_list_generated.json.")
         json.dump(data,json_file,indent=4)

    return 1
    #return response
    


def take_snapshot(uuid,cip):
    with open("prism_element_creds.json", 'r') as file:
    # Load the JSON data
        data = json.load(file)
    print(data)
    headers = {"Content-Type": "application/json", "charset": "utf-8"}
    endpoint = "https://10.38.87.37:9440/PrismGateway/services/rest/v2.0/snapshots/"
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    snapshot_name = "snapshot-"+str(datetime.now())
    body = {
        "snapshot_specs":[
            {
                "snapshot_name":snapshot_name,
                "vm_uuid":uuid

            }
        ]
    }
    #response = requests.post(endpoint,auth=(user, passw),headers=headers,verify=False,data=json.dumps(body))
    for obj in data:
        if cip == obj["ip"]:
            print(obj)
            endpoint = "https://{}:9440/PrismGateway/services/rest/v2.0/snapshots/".format(cip)
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            user = obj["username"]
            passw = obj["password"]
            response = requests.post(endpoint,auth=(user, passw),headers=headers,verify=False,data=json.dumps(body))
            print(response.status_code)
            print(response.json())
            if response.status_code == 201:
                return response
            else:
                return None
            
            
        

def get_vm_uuidsc(creds):
    with open("pe_list_generated.json", 'r') as file:
    # Load the JSON data
        data = json.load(file)
    #print(data)
    uuid_ip = {}
    for obj in data:
        uuid_ip[obj["uuid"]] = obj["ip"]
        #uuid_ip.append(item)

    #print(uuid_ip)
    PC_IP = creds[0]
    user=creds[1]
    passw=creds[2]
    headers = {"Content-Type": "application/json", "charset": "utf-8"}
    endpoint = "https://{}:9440/api/nutanix/v3/vms/list".format(PC_IP)
    #print(creds)
    #endpoint  = "https://{}:9440/PrismGateway/services/rest/v2.0/vms/".format(PE_IP)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    body = {"kind":"vm","length":500}
    try:
        response = requests.post(endpoint,auth=(user, passw),headers=headers,verify=False,data=json.dumps(body))
        if response.status_code != 200:
            return None
    except TimeoutError:
        return None
    #print(response.status_code)
    vms_uuid = []
    vm_count = 0
    #print(list(response.json()))
    #print(list(response.json()["metadata"]))
    #return
    for obj in response.json()["entities"]:
        item = {}
        item["vm_name"] = obj["status"]["name"]
        item["uuid"] = obj["metadata"]["uuid"]
        item["cip"] = uuid_ip[obj["spec"]["cluster_reference"]["uuid"]]
        vms_uuid.append(item)
        vm_count+=1
    obj = {}
    obj["Vm_count"] = vm_count
    vms_uuid.append(obj)
        #vms_uuid.append(item)
    #print(vms_uuid)
    vms_uuid = sorted(vms_uuid, key=lambda x: x.get('cip', ''))

    with open("pc_generated_vms_uuid.json","w") as json_file:
         print("VMS data fetched from PC and saved in pc_generated_vms_uuis.json.")
         json.dump(vms_uuid,json_file,indent=4)
    return []

#creds = ["10.38.87.39","rushabh","Nutanix/4u"]
#get_pe(creds)
#get_vm_uuidsc(creds)
#take_snapshots(creds)
#get_pe(creds=creds)
#get_vms()
#get_vms_form_pe()
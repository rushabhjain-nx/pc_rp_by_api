from flask import Flask, render_template, request, redirect, url_for
from script import get_vm_uuidsc,get_pe,take_snapshot,get_vms_form_pe
app = Flask(__name__)
import json
import requests
import urllib3

selected_items = []
creds = []

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process_pe', methods=['POST'])
def process_pe():
    print(list(request.form))
    n = int(len(request.form)/4)
    print(n)
    data=[]
    for i in range(1,n+1):
        item={}
        item["uuid"] = request.form["uuid"+str(i)].strip()
        item["username"] = request.form["username"+str(i)].strip()
        item["password"] = request.form["password"+str(i)].strip()
        item["ip"] =  request.form["ip"+str(i)].strip()
        data.append(item)

    headers = {"Content-Type": "application/json", "charset": "utf-8"}
    for obj in data:
        endpoint = "https://{}:9440/PrismGateway/services/rest/v2.0/clusters/".format(obj["ip"])
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        user = obj["username"]
        passw = obj["password"]
        response = requests.get(endpoint,auth=(user, passw),headers=headers,verify=False)
       
        if response.status_code != 200:
                print("Invalid Credentials for IP :",obj["ip"])
                #print(obj["ip"])
                #print("Credentials for ",+str(obj["ip"])+" are Incorrect!")
                return redirect(url_for('invalid_pe'))
        

    with open("prism_element_creds.json","w") as json_file:
         json.dump(data,json_file,indent=4)
         print("Prism Element Credentials Saved in prism_element_creds.json")

    res = get_vms_form_pe()
    if res==None:
        #print("PLEASE ENTER CORRECT CREDENTIALS")
        return redirect(url_for('error_page'))



    return redirect(url_for('display_data'))


@app.route('/invalid_pe')
def invalid_pe():
    return render_template('invalid_pe.html')



@app.route('/process_form', methods=['POST'])
def process_form():
    global creds
    creds = []
    field1 = request.form['field1']
    field2 = request.form['field2']
    field3 = request.form['field3']
    creds.append(field1.strip())
    creds.append(field2.strip())
    creds.append(field3.strip())
    #print(field1,field3)
    print(creds)
    res = get_pe(creds=creds)
    if res==None:
        print("PLEASE ENTER CORRECT PC CREDENTIALS")
        return redirect(url_for('error_page'))
        
    
        
    #added new line for pe
    
     
    global selected_items
    selected_items = request.form.getlist('selected_items')
    return redirect(url_for('pe_creds'))

@app.route('/pe_creds')
def pe_creds():
    j_file = "pe_list_generated.json"
    with open(j_file, 'r') as file:
        data = json.load(file)
    print(data)
    return render_template('pe.html', data=data)



@app.route('/display_data', methods=['POST','GET'])
def display_data():
    j_file = "vms_from_pe.json"
    with open(j_file, 'r') as file:
        data = json.load(file)
    #print(data)
    return render_template('display_data.html', data=data)

@app.route('/error_page')
def error_page():
    return render_template('error_page.html')

@app.route('/final_submit', methods=['POST'])
def final_submit():
    selected_items = request.form.getlist('selected_items[]')
    #vm_names = request.form.getlist('vm_name[]')
    #vm_uuids = request.form.getlist('vm_uuid[]')
    print("Selected Items:", selected_items)
    #print(creds)
    final_data = []
    
    for item in selected_items:
        temp = item.split("|")
        uuid = temp[0]
        cip = temp[1]
       
        #print(uuid,cip)
        obj = {}
        res = take_snapshot(uuid,cip)
        obj["vm_uuid"] = uuid
        obj["vm_name"] = temp[2]
        if res == None:
            obj["task_uuid"] = "Error In Operation"
        
        else:
            obj["task_uuid"] = res.json()['task_uuid']
        #print(obj)
        final_data.append(obj)
        #print(res.json())
    
    with open("vm_uuid_and_snapshot_task.json","w") as json_file:
         json.dump(final_data,json_file,indent=4)

    return render_template('final_submit.html', final_data=final_data)


if __name__ == '__main__':
    app.run(debug=True,port=9000)

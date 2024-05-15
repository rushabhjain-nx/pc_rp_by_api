from flask import Flask, render_template, request, redirect, url_for
from script import get_vm_uuidsc,take_snapshots,get_pe
app = Flask(__name__)
import json


selected_items = []
creds = []

@app.route('/')
def index():
    return render_template('index.html')

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
    res = get_vm_uuidsc(creds)
    if res==None:
        print("PLEASE ENTER CORRECT CREDENTIALS")
        return redirect(url_for('error_page'))
        return
    #added new line for pe
    get_pe(creds=creds)
    
    global selected_items
    selected_items = request.form.getlist('selected_items')
    return redirect(url_for('display_data'))

@app.route('/display_data')
def display_data():
    j_file = "pc_generated_vms_uuid.json"
    with open(j_file, 'r') as file:
        data = json.load(file)
    #print(data)
    return render_template('display_data.html', data=data)

@app.route('/error_page')
def error_page():
    return render_template('error_page.html')

@app.route('/final_submit', methods=['POST'])
def final_submit():
    selected_items = request.form.getlist('selected_items')
    print(selected_items)
    #print(creds)
    final_data = []
    
    for uuid in selected_items:
        obj = {}
        res = take_snapshots(creds,uuid)
        obj["vm_uuid"] = uuid
        obj["task_uuid"] = res.json()['task_uuid']
        print(obj)
        final_data.append(obj)
        #print(res.json())
    with open("vm_uuid_and_snapshot_task.json","w") as json_file:
         json.dump(final_data,json_file,indent=4)

    return render_template('final_submit.html', final_data=final_data)


if __name__ == '__main__':
    app.run(debug=True,port=9000)

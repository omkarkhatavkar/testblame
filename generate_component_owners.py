import yaml

member_list = dict()
with open(r'/tmp/component-owners-map.yaml') as file:
    user_list = yaml.load(file, Loader=yaml.FullLoader)
    for _, doc in user_list.items():
        member_list[doc['slug']] =  doc['primary']
import json
with open('/tmp/testimony.json') as data_file:    
    data = json.load(data_file)
json_list = {}
file_paths={}
for input_data in data:
    if not input_data['_testimony']['file-path'] in file_paths:
        file_paths[input_data['_testimony']['file-path']] = 1
        if input_data['casecomponent'].lower() in member_list:
            if not member_list[input_data['casecomponent'].lower()] in json_list:
                json_list[member_list[input_data['casecomponent'].lower()]] = [input_data['_testimony']['file-path']]
            else:
                list = json_list[member_list[input_data['casecomponent'].lower()]]
                list.append(input_data['_testimony']['file-path'])
import json
with open('robottelo_component.json', 'w') as fp:
    json.dump(json_list, fp)


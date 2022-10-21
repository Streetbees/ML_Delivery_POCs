import json

def read_json_as_dict(json_file_name:str):
    with open(json_file_name) as d:
        dict_name = json.load(d)
    return dict_name
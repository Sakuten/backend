import json
import random


maximum_id = 148955


class IDServer:
    def __init__(self, json_path):
        self.json_path = json_path
        with open(json_path, 'r') as f:
            json_data = json.load(f)
            self.unused_id_list = json_data["ids"]

    def pop(self):
        return self.unused_id_list.pop()

    def update_json_file(self):
        writeJson(self.json_path, self.unused_id_list)


def writeJson(json_path, ids):
    def id_list2json(ids):
        return json.dumps({"ids": ids}, indent=4)

    with open(json_path, 'w') as f:
        f.write(id_list2json(ids))


def generateIDJsonFile(json_path, how_many):
    ids = random.sample(range(maximum_id), how_many)
    writeJson(json_path, ids)

import json

class JsonLoader(object):

    def load(self, path):
        with open(path, 'r', encoding='utf-8') as jsonfile:
            return json.loads(jsonfile.read())
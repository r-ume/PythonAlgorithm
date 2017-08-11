import json

jsonString = '''
{
    "name": "aaa",
    "age": 30
}
'''
data = json.loads(jsonString)
print(data) # {u'age': 30, u'name': u'aaa'}
print(data["name"]) # aaa

import json
import requests
from requests_oauthlib import OAuth1

url = 'https://api.bricklink.com/api/store/v1/items/SET/10404-1/subsets'

auth = OAuth1('CF88082C235A44668F011186D7B05AA4', '427F8BA0E13C49E7AD626FF803C56EC5', 'B88B6FBCA537491B9B276A9E46D252A7', '54800B48AD8C4B0A97ABB5C7050EF15D')

reqSession = requests.get(url, auth=auth)
#print(reqSession.text)
blCategories = json.loads(reqSession.text)

#json.dump(blCategories, "C:\\Users\\Spongeloaf\\Google Drive\\peter\\python projects\\machine learning\\dumps\\blCatJson.txt")

with open("C:\\Users\\Spongeloaf\\Google Drive\\peter\\python projects\\machine learning\\dumps\\blPartJson.json", 'w') as outfile:
    json.dump(blCategories, outfile, sort_keys = True, indent = 2)
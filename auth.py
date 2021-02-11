import gkeepapi
import json
import sys

print(sys.argv[1])
username, password = sys.argv[1].split()

keep = gkeepapi.Keep()

keep.login(username, password)
token = keep.getMasterToken()
data = {'username': username, 'password': password, 'token': token}
json.dump({'username': username, 'password': password, 'token': token}, open('token.json', 'w'))
state = keep.dump()
fh = open('notes.json', 'w')
json.dump(state, fh)

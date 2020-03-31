import json
from urllib.request import urlopen, quote

# using map Api
def getlnglat(address):

    url = 'http://api.map.baidu.com/geocoder/v2/?address='
    output = 'json'
    add = quote(address)
    url2 = url + add + '&output=' + output + "&ak=" + 'oFLG0o9n50jNNjuFfuDTOE6gqjGG2p1t'
    req = urlopen(url2)
    res = req.read().decode()
    temp = json.loads(res)

    try:
        log = temp['result']['location']['lng']
        lat = temp['result']['location']['lat']
    except:
        log = 0
        lat = 0

    return log, lat




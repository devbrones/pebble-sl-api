from flask import Flask, request
import json
import requests
from config import config
import time
import string
import random

app=Flask(__name__)

class apikeys:
    stoplookup = "750a9ec2bf6b421988dfc6977561aa5b"
    departures = "19a25c00721e4d57a8bf175db7985520"

def getSiteId(term):
    if config.debug:
        print("getting siteid of stop: " + config.stops[term])
    try:
        r=requests.get(config.stoplookup_return_url(config, apikeys.stoplookup, config.stops[term]))
        siteid = r.json()["ResponseData"][0]["SiteId"]
        if config.debug:
            print("got siteid: " + siteid + " for stop: " + config.stops[term])
        return siteid
    except IndexError as e:
        print("no data")
        return 1

def getDepartures(siteid):
    if siteid == 1:
        return 1
    if config.debug:
        print("getting departures / arrivals of siteid: " + str(siteid))
    r=requests.get(config.departures_return_url(config, apikeys.departures, siteid, 20))
    ad = [r.json()["ResponseData"]["Buses"], r.json()["ResponseData"]["Metros"]]
    return ad

def departureParser(deplist):
    departures_bus=[]
    departures_metro=[]
    i = 0
    for d in deplist:
        i += 1
        for x in d:
            if x["LineNumber"] in config.idents_bus or x["LineNumber"] in config.idents_metro:
                line=x["LineNumber"]
                dest=x["Destination"]
                stop=x["StopAreaName"]
                time=x["DisplayTime"]
                acct=x["ExpectedDateTime"]
                if i == 1:
                    departures_bus.append([line,dest,stop,time,acct])
                elif i != 1:
                    departures_metro.append([line,dest,stop,time,acct])
    return [departures_bus, departures_metro]

def generateUUID(length):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(0,length))

def send_ProviderNTFY(obj, shorthand=True): # obj: self explanatory, shorthand: whether or not obj is short version
    if obj == [[]]:
        return 1
    if shorthand:
        dat1 = []
        data = ""
        for i in range(0,len(obj)):
            dat=str(str(obj[i][0]) + ": " + str(obj[i][1]) + " | " + str(obj[i][2]))
            dat1.append(dat)
        for j in dat1:
            data += str(" " + j)
        r = requests.put(str("http://ntfy.sh/sl-new-event"), json=data)
        return 0
    data=str(str(str(obj[0]) + " " + str(obj[1]) + " @ " + str(obj[2]) + " in " + str(obj[3])))#.encode("ascii", "replace")
    r = requests.put(str("http://ntfy.sh/sl-new-event"), json=data)

def send_ProviderLocal(obj, shorthand=True):
    #print(obj)
    if obj == [[]]:
        return 1
    if shorthand:
        dat1 = []
        data = ""
        print(len(obj))
        for i in range(0,len(obj)):
            print(obj)
            dat=str(str(obj[i][0]) + ": " + str(obj[i][1]) + " | " + str(obj[i][2])+"----------0-- \U0001F636 --0----------")
            print(dat)
            dat1.append(dat)
        for j in dat1:
            if not data:
                data += str("" + j)
            elif data:
                data += str("" + j)


        return data
    data=str(str(str(obj[0]) + " " + str(obj[1]) + " @ " + str(obj[2]) + " in " + str(obj[3])))#.encode("ascii", "replace")
    return data




def constructMessage(obj, n=3): # obj: list to format, n: length of output (in lines)
    alles=[]
    if len(obj) < n:
        n = len(obj)
    for i in range(0, n):
        new = [obj[i][0], obj[i][1], obj[i][3]]
        if config.debug:
            #print(new)
            a=1
        alles.append(new)
    return alles





def main(s):
    s = int(s)
    actual_departures = departureParser(getDepartures(getSiteId(s)))
    print(type(actual_departures))
    print(type(actual_departures))
    if len(actual_departures[0]) > 0 and len(actual_departures[1]) > 0:  # both bus and metro departures
        if config.ntfy_framework:
            send_ProviderNTFY(constructMessage(actual_departures[0]))
            send_ProviderNTFY(constructMessage(actual_departures[1]))
            return 'OK\n'
        else:
            return str(send_ProviderLocal(
                constructMessage(
                    actual_departures[0]
                )
            ))+str(
                (
                    send_ProviderLocal(
                        constructMessage(
                            actual_departures[1]
                        )
                    )
                )
            )
    if len(actual_departures[0]) > 0 and len(actual_departures[1]) == 0: # only bus
        if config.ntfy_framework:
            send_ProviderNTFY(constructMessage(actual_departures[0]))
            return 'OK\n'
        else:
            return send_ProviderLocal(constructMessage(actual_departures[0]))
    if len(actual_departures[0]) == 0 and len(actual_departures[1]) > 0: # only metro
        if config.ntfy_framework:
            send_ProviderNTFY(str(constructMessage(actual_departures[1])))
            return 'OK\n'
        else:
            return send_ProviderLocal(constructMessage(actual_departures[1]))

    time.sleep(5)







@app.route('/', methods=['POST','GET'])
def sendPing():
    stop = request.args.get('s')
    print(main(stop))
    return main(stop)

app.run(host='0.0.0.0')

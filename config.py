class config:
    _version=""
    version=""
    ntfy_framework=False
    debug=True
    stops=["Vikdalsvägen","Björkhagen","Slussen"]
    idents_bus=["443","71","840","443c"]
    idents_metro=["17"]
    timewindow="20" # how many minutes we want returned of departures
    def stoplookup_return_url(self, key, term):
        stoplookup_url=str("https://api.sl.se/api2/typeahead.json?key="+key+"&searchstring="+term+"%&stationsonly=True")
        return stoplookup_url
    def departures_return_url(self, key, siteid, time):
        departures_url=str("https://api.sl.se/api2/realtimedeparturesV4.json?key="+key+"&siteid="+siteid+"&timewindow="+str(time))
        return departures_url

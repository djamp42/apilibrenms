import requests
import json
import re


class LibrenmsApi:

    """ Init: builds the API call, IP/API KEY
    """
    def __init__(self, librenmsip, librenmskey):
        """ Constructor for this class. """
        if librenmsip.startswith("http"):
            self.api_url = f"{librenmsip}/api/v0/"
        else:
            self.api_url = f"http://{librenmsip}/api/v0/"
        self.request_headers = {"Content-Type": "application/json",
                                "Accept-Language": "en-US,en;q=0.5",
                                "User-Agent": "djamp42 LibreNMS Python API",
                                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                                "X-Auth-Token": librenmskey,
                                "Connection": "keep-alive"
                                }

    # Read Requests
    def readlocations(self):
        """ Return a list of all LibreNMS locations."""
        api_url = f"{self.api_url}resources/locations"
        r = requests.get(api_url, headers=self.request_headers)
        locations = json.loads(r.text)["locations"]
        return locations

    def locationsearch(self, searchrequest):
        """ Return list of devices that match the LibreNMS location searched for """
        api_url = f"{self.api_url}devices?type=location&query={searchrequest}"
        r = requests.get(api_url, headers=self.request_headers)
        devicelist = json.loads(r.text)["devices"]
        return devicelist

    def listalldevices(self):
        """ Return list of all devices in LibreNMS """
        api_url = f"{self.api_url}devices/"
        r = requests.get(api_url, headers=self.request_headers)
        devices = json.loads(r.text)["devices"]
        return devices

    def readdevice(self, hostname):
        """ Return device """
        api_url = f"{self.api_url}devices/{hostname}"
        r = requests.get(api_url, headers=self.request_headers)
        devices = json.loads(r.text)["devices"][0]
        return devices

    def readdeviceports(self, hostname, dbcolumn):
        """ Return device """
        api_url = f"{self.api_url}devices/{hostname}/ports?columns={dbcolumn}"
        r = requests.get(api_url, headers=self.request_headers)
        ports = json.loads(r.text)["ports"]
        return ports

    def ipv4networks(self):
        api_url = f"{self.api_url}resources/ip/networks"
        r = requests.get(api_url, headers=self.request_headers)
        ipv4networks = json.loads(r.text)["ip_networks"]
        return ipv4networks

    def deviceipaddress(self, hostname):
        api_url = f"{self.api_url}devices/{hostname}/ip"
        r = requests.get(api_url, headers=self.request_headers)
        ipaddress = json.loads(r.text)["addresses"]
        return ipaddress

    def devicegrpread(self, devicegrp):
        api_url = f"{self.api_url}devicegroups/{devicegrp}"
        r = requests.get(api_url, headers=self.request_headers)
        device_ids = json.loads(r.text)["devices"]
        return device_ids

    def devicegrps(self):
        api_url = f"{self.api_url}devicegroups"
        r = requests.get(api_url, headers=self.request_headers)
        devicegrps = json.loads(r.text)
        return devicegrps

# PORT API Calls
    def readport(self, portid):
        api_url = f"{self.api_url}ports/{portid}"
        r = requests.get(api_url, headers=self.request_headers)
        port = json.loads(r.text)["port"][0]
        return port

    def portsearch(self, searchreq):
        api_url = f"{self.api_url}ports/search/{searchreq}"
        r = requests.get(api_url, headers=self.request_headers)
        portlist = json.loads(r.text)["ports"]
        return portlist

    def portgroupgraph(self, description, width, height):
        api_url = f"{self.api_url}portgroups/{description}?width={width}&height={height}"
        r = requests.get(api_url, headers=self.request_headers)
        return r.text

    def portgraph(self, hostname, ifname, graphtype, width, height, startgraph, endgraph):
        api_url = f"{self.api_url}devices/{hostname}/ports/{ifname}/{graphtype}?width={width}&height={height}&from={startgraph}&to={endgraph}"
        r = requests.get(api_url, headers=self.request_headers)
        # Strip Height and Width from SVG to make graph CSS Responsive
        finalportgraph = self.svgstrip(r.text)
        return finalportgraph

# WIRELESS API CALLS
    def wirelessgraph(self, hostname, graphtype):
        api_url = f"{self.api_url}devices/{hostname}/graphs/wireless/{graphtype}"
        r = requests.get(api_url, headers=self.request_headers)
        # Strip Height and Width from SVG to make graph CSS Responsive
        finalportgraph = self.svgstrip(r.text)
        return finalportgraph

    # Write Requests
    def device_add(self, add_request):
        api_url = f"{self.api_url}devices"
        r = requests.post(api_url, json=add_request, headers=self.request_headers)
        return r.text
    def device_del(self, del_request):
        api_url = f"{self.api_url}devices/{del_request}"
        r = requests.delete(api_url, headers=self.request_headers)
        return r.text

    def device_update(self, hostname, update_request):
        api_url = f"{self.api_url}devices/{hostname}"
        r = requests.patch(api_url, json=update_request, headers=self.request_headers)
        return r.text

    # Other Stuff
    def svgstrip(self, svgdata):
        """ Strip Height and Width from SVG to make graph CSS Responsive """
        rm_width = re.sub(' width="(.*?)"', "", svgdata)
        svgfinal = re.sub(' height="(.*?)"', "", rm_width)
        return svgfinal


class LibrenmsFilter:

    """ Init: This is to filter devices from a device list generated by LibreNMS API.
    """
    def __init__(self, devicelist, filterup=True):
        """INIT the libernms Filter
        1) Set filterup to true to remove down devices from filter list
        """
        self.filterlist = []
        if filterup:
            self.devicelist = self.upfilter(devicelist)
        else:
            self.devicelist = devicelist

    def upfilter(self, devicelist):
        """ Filters out down device from device list"""
        upfilter = []
        for devicedict in devicelist:
            if devicedict['status'] == 1:
                upfilter.append(devicedict)
        return upfilter

    def hardwarefilter(self, devicehwlist):
        """Filters device list based on hardware list"""
        for devicedict in self.devicelist:
            # ignore device without hardware
            if not devicedict["hardware"]:
                continue
            else:
                for hardware in devicehwlist:
                    if devicedict["hardware"].startswith(hardware):
                        self.filterlist.append(devicedict)
        return self.filterlist

    def featurefilter(self, featurelist):
        """Filter device list based on feature list"""
        for devicedict in self.devicelist:
            # ignore device without features
            if not devicedict["features"]:
                continue
            else:
                for feature in featurelist:
                    if devicedict["features"].startswith(feature):
                        self.filterlist.append(devicedict)
        return self.filterlist

    def versionfilter(self, versionlist):
        """Filter device list based on verison"""
        for devicedict in self.devicelist:
            # ignore device without verison
            if not devicedict["version"]:
                continue
            else:
                for version in versionlist:
                    if devicedict["version"].startswith(version):
                        self.filterlist.append(devicedict)
        return self.filterlist

    def ipfilter(self, iplist):
        """Filter device list based on ip address list"""
        for devicedict in self.devicelist:
            for ip in iplist:
                if devicedict["hostname"].startswith(ip):
                    self.filterlist.append(devicedict)
        return self.filterlist


class LibrenmsLocFilter:
    def __init__(self):
        self.filterloclist = []

    def firstcommafilter(self, locationlist):
        for sitename in locationlist:
            sitefirstcomma = re.match("[^,]*", sitename["location"])
            self.filterloclist.append(sitefirstcomma.group())
        # List dedup
        filterloclistdedup = list(set(self.filterloclist))
        filterloclistdedup.sort()
        return filterloclistdedup

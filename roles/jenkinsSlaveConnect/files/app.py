import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import xml.etree.ElementTree as ET
import argparse

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
parser = argparse.ArgumentParser()
required = parser.add_argument_group('required arguments')
required.add_argument("--ostype", "-t", help="set OS type as windows or linux")
required.add_argument("--url", "-url", help="set Jenkins URL.")
required.add_argument("--username", "-u", help="set Jenkins username.")
required.add_argument("--password", "-p", help="set Jenkins password.")

args = parser.parse_args()

# Store Arguments 
ostype=args.ostype
jenkinsUrl=args.url
username=args.username
password=args.password


def getRequest(url,username,password):
    return requests.get(url,auth=(username,password), verify=False)

def postRequest(url,username,password):
    return requests.post(url, auth=(username,password), verify=False)

# Get list of slaves from Jenkins

url=jenkinsUrl+'/computer/api/json'
jsonString = getRequest(url,username,password)
r=json.loads(jsonString.text)
for result in r['computer']:
        if(result['displayName'] != 'master' and result['offline']):
                slaveInfoUrl=jenkinsUrl+'/computer/'+result['displayName']+'/config.xml'
                slaveInfoResponse=getRequest(slaveInfoUrl,username,password)
                root=ET.fromstring(slaveInfoResponse.text)
                slaveInfoWorkspace=root.find(".//remoteFS").text
                reconnectUrl=jenkinsUrl+'/computer/'+result['displayName']+'/launchSlaveAgent'
                if(":" in slaveInfoWorkspace and ostype=='windows'):
                    print 'Restarting Agent '+result['displayName']+' using api '+reconnectUrl+' ...'
                    response=postRequest(reconnectUrl,username,password)
                elif(":" not in slaveInfoWorkspace and ostype=='linux'):
                    print 'Restarting Agent '+result['displayName']+' using api '+reconnectUrl+' ...'
                    response=postRequest(reconnectUrl,username,password)

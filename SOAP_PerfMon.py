import requests
import json
from requests.auth import HTTPBasicAuth
from xml.etree import ElementTree
from datetime import datetime
import os

devices = [
    'MTP',
    'HW Conference Bridge',
    'SW Conference Bridge',
    'Transcode'
]

CMserver = ['10.62.150.183', '10.62.150.184']
serv_user = 'perfmon'
serv_pass = 'soap'
basedir = '/opt/wcy/'

soap_query = '<?xml version="1.0" encoding="UTF-8"?> \
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:soap="http://schemas.cisco.com/ast/soap"> \
   <soapenv:Header/> \
   <soapenv:Body> \
      <soap:perfmonCollectCounterData> \
         <soap:Host>{}</soap:Host> \
         <soap:Object>Cisco {} Device</soap:Object> \
      </soap:perfmonCollectCounterData> \
   </soapenv:Body> \
</soapenv:Envelope>'

headers = {'Content-Type': 'text/xml; charset=utf-8',
           'SOAPAction': '"http://schemas.cisco.com/ast/soap/action/#PerfmonPort#PerfmonCollectCounterData"'
          }

json_data = json.dumps({})
my_dict = {}
my_list = []

s_timestamp = str((datetime.now() - datetime(1970, 1, 1)).total_seconds())
s_timestamp = s_timestamp.split('.')[0]
s_datetime = str(datetime.now())[0:-7]

date_s = str(datetime.now()).split(' ')[0].split('-')
time_s = str(datetime.now()).split(' ')[1][0:-7].split(':')
dir_s = date_s[0] + date_s[1] + date_s[2]
file_suff = dir_s + time_s[0] + time_s[1] + time_s[2]

for ccm in CMserver:
    for device in devices:
        data = soap_query.format(ccm, device)
        response = requests.post('https://' + ccm + ':8443/perfmonservice2/services/PerfmonService', data=data,
                             headers=headers, auth=HTTPBasicAuth(serv_user, serv_pass), verify=False)

        tree = ElementTree.fromstring(response.text)

        for dev in tree.findall(".//{http://schemas.cisco.com/ast/soap}perfmonCollectCounterDataReturn"):
            my_dict['timestamp'] = s_timestamp
            my_dict['datetime'] = s_datetime
            my_dict['Name'] = dev.find('.//{http://schemas.cisco.com/ast/soap}Name').text
            my_dict['Value'] = dev.find('.//{http://schemas.cisco.com/ast/soap}Value').text
            my_dict['Status'] = dev.find('.//{http://schemas.cisco.com/ast/soap}CStatus').text
            my_list.append(my_dict.copy())

json_data = json.dumps(my_list, sort_keys=True)

if not os.path.exists(basedir + dir_s):
    os.makedirs(basedir + dir_s)

filepath = os.path.join(basedir, dir_s, 'MediaResources.'+file_suff)
file = open(filepath, 'w')
file.write(str(json_data))
file.close()

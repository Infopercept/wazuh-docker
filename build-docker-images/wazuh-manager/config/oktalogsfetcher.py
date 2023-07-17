'''
1: Use python3
2: If you're running script for a first time it'll start fetching logs until there are none left to fetch. and then it'll keep on running and fetching new logs forever
3: Make sure to clear output.log file every time you run this script, otherwise there will be duplicated log entries.
'''

import requests
import logging
import json
import time
import configparser
from datetime import date, datetime

file_name = "output.log" # fetching logs into this file
script_logs_file = "oktascript.log" # check script logs in this file


logging.basicConfig(filename=script_logs_file,
                    format='%(asctime)s %(message)s',
                    filemode='a')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def get_logs(org, token, limit, sleep):

    if(int(limit) > 1000):
        limit = '1000'

    start_date = datetime.utcnow().isoformat()
    #start_date = date.today().isoformat()
    #start_date="2022-09-16T11:25:28.913Z"
    checkpoint_url = ""

    headers = {
      'Authorization': f'SSWS {token}'
    }

    while True:

        if len(checkpoint_url) > 0:    #warm start
            url = checkpoint_url
        else:                 #cold start
            logging.info("[INFO] Cold start...")
            url = f"https://{org}.okta.com/api/v1/logs?&limit={limit}&since={start_date}&sortOrder=ASCENDING"

        while url:
            try:
                response = requests.request("GET", url, headers=headers, data={})
            except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
                logging.error(f"[ERROR] Something else: {e}")

            logging.info(f"[INFO] API response length:{len(response.json())}")

            if len(response.json()) == limit and 'next' in response.links:
                url = response.links['next']['url']
                write_to_file(response.json())

            elif len(response.json()) == 0:
                checkpoint_url = url
                url = False
            else:
                checkpoint_url = response.links['next']['url']
                write_to_file(response.json())
                url = False

        logging.info(f"sleeping for {sleep} seconds...")
        time.sleep(int(sleep))

def write_to_file(json_data):
    result = {"oktalogsall":{},"oktaintegration":"oktalogsall"}
    if json_data:
        with open(file_name, "a") as f:
            for stuff in json_data:
                #if stuff.get("target").get("displayName"):
                #    result["oktalogsall"]["displayNameUser"]=stuff.get("target").get("displayName")
                #    print(result)
                #if stuff.get("target").get("alternateId"):
                #    result["oktalogsall"]["alternateId1"]=stuff.get("target").get("alternateId")
                #    print(result)
                if stuff.get("target"):
                    #print("in target")
                    #print("len of gtarget = ",len(stuff.get("target")))
                    if len(stuff.get("target")) == 1:
                        #print("insdie len 1")
                        stuff["displayNameUser0"]=stuff.get("target")[0].get("displayName")
                        #result["oktalogsall"]["displayNameUser0"]=stuff.get("target")[0].get("displayName")
                        #print("displyaname in target:",stuff.get("target")[0].get("displayName"))
                        stuff["alternateIdEmail0"]=stuff.get("target")[0].get("alternateId")
                        #result["oktalogsall"]["alternateIdEmail0"]=stuff.get("target")[0].get("alternateId")
                    if len(stuff.get("target")) > 1:
                        #print("inside len >1")
                        counter = 0
                        for i in stuff.get("target"):
                            stuff[f"displayNameUser{counter}"]= i.get("displayName")
                            stuff[f"alternateIdEmail{counter}"]=i.get("alternateId")
                            counter += 1
                    del stuff["target"]
                if stuff.get("transaction").get("type"):
                    del stuff["transaction"]["type"]
                if stuff.get("client"):
                    if stuff.get("client").get("geographicalContext"):
                        stuff["client"]["geoContext"] = stuff["client"]["geographicalContext"]
                        del stuff["client"]["geographicalContext"]
                        #if stuff.get("client").get("geographicalContext").get("geolocation"):
                        #    del stuff["client"]["geographicalContext"]["geolocation"]
                        #if stuff.get("client").get("geographicalContext").get("city"):
                        #    del stuff["client"]["geographicalContext"]["city"]
                        #if stuff.get("client").get("geographicalContext").get("state"):
                        #    del stuff["client"]["geographicalContext"]["state"]
                        #if stuff.get("client").get("geographicalContext").get("postalCode"):
                        #    del stuff["client"]["geographicalContext"]["postalCode"]
                    if stuff.get("client").get("userAgent"):
                        del stuff["client"]["userAgent"]
                        #if stuff.get("client").get("userAgent").get("rawUserAgent"):
                        #    del stuff["client"]["userAgent"]["rawUserAgent"]
                        #if stuff.get("client").get("userAgent").get("os"):
                        #    stuff["client"]["userAgent"]["os"] = stuff.get("client").get("userAgent").get("os").replace(" ", "-")
                result.update({"oktalogsall":stuff})
                json.dump(result, f)
                f.write("\n")
    else:
        return

################################# Driver code
try:
    config = configparser.RawConfigParser()
    config.readfp(open('okta-config.properties'))
    org = config.get("Config", "org")
    token = config.get("Config", "token")
    rest_record_limit = int(config.get("Config", "restRecordLimit"))
    sleep_time = config.get("Config","sleepTime")
except:
    print("[Error] okta-config.properties file not found or parsing error")

print(get_logs(org, token, rest_record_limit, sleep_time))
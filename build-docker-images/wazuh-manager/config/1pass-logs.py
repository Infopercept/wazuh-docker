import requests
import time
import json
import configparser
import logging
import os
#import sys

script_logs_file = "/var/ossec/logs/1password-script.log" # check script logs in this file
filename = "/var/ossec/logs/1password-logs.log" # check 1password logs in this file

logging.basicConfig(filename=script_logs_file,
                    format='%(asctime)s %(message)s',
                    filemode='a')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

########## 1PASSWORD CONFIG DATA #######################
try:
    config = configparser.RawConfigParser()
    config.read('/var/ossec/etc/1pass-config.properties')
#    token = config.get("Config", "token")
    base_url = config.get("Config", "baseUrl")
    sleep_time = int(config.get("Config", "sleepTime"))
    sigin_attempts = config.get("Config", "signinAttempts")
    item_usage = config.get("Config", "itemUsages")
    audit_events = config.get("Config", "auditEvents")
except Exception as e:
    logging.error(f"[Error] {e}")
    exit(1)
token = os.getenv("ONEPASS_API_KEY")
if token and  len(token) < 0:
    print("Unable to get token env")
    exit(1)

#######################################################

def _parse_api_response(response):
    if response.status_code == 200:
        if len(response.json()["items"]) > 0:
            return response.json()["items"]
        else:

            return False
    else:
        logging.error(f"[Error] No items in response")
        return False

def _write_to_file(data):
    with open(filename, "a") as f:
        for item in data:
            f.write(f"{json.dumps(item)}\n")

def fetch_logs():
    sign_in_url = base_url + "/api/v1/signinattempts"
    items_usage_url = base_url + "/api/v1/itemusages"
    audit_events_url = base_url + "/api/v1/auditevents"

    sign_in_cursor = ""
    items_usage_cursor = ""
    audit_events_cursor = ""

    headers = {"Content-Type": "application/json","Authorization": f"Bearer {token}"}

    while True:
        if sigin_attempts == "true":
            logging.info("[INFO] Getting signin attempts.....")
            body = {"cursor": str(sign_in_cursor)}
            try:
                r = requests.post(sign_in_url, headers=headers, json=body if len(sign_in_cursor) > 0 else {})
                sign_in_cursor = r.json()["cursor"]
            except requests.exceptions.RequestException as e:
                logging.error(f"[ERROR] {e}")

            signin_data = _parse_api_response(r)
            if signin_data != False:
                logging.info(f"[INFO] Signin logs len: {len(signin_data)}")
                _write_to_file(signin_data)
            else:
                logging.info("[INFO] No new signin attempts events")

        if audit_events == "true":
            logging.info("[INFO] Getting audit events.....")
            body = {"cursor": str(audit_events_cursor)}
            try:
                r = requests.post(audit_events_url, headers=headers, json=body if len(audit_events_cursor) > 0 else {})
                audit_events_cursor = r.json()["cursor"]
            except requests.exceptions.RequestException as e:
                logging.error(f"[ERROR] {e}")

            audit_events_data = _parse_api_response(r)
            if audit_events_data != False:
                logging.info(f"[INFO] Audit logs len: {len(audit_events_data)}")
                _write_to_file(audit_events_data)
            else:
                logging.info("[INFO] No new audit events")

        if item_usage == "true":
            logging.info("[INFO] Getting itemusage events.....")
            body = {"cursor": str(items_usage_cursor)}
            try:
                r = requests.post(items_usage_url, headers=headers, json=body if len(items_usage_cursor) > 0 else {})
                items_usage_cursor = r.json()["cursor"]
            except requests.exceptions.RequestException as e:
                logging.error(f"[ERROR] {e}")

            item_usage_data = _parse_api_response(r)
            if item_usage_data != False:
                logging.info(f"[INFO] Item usage logs len: {len(item_usage_data)}")
                _write_to_file(item_usage_data)
            else:
                logging.info("[INFO] No new item usage events")

        logging.info(f"[INFO] Sleeping for {sleep_time} seconds")
        time.sleep(int(sleep_time))

logs = fetch_logs()

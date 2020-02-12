#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import csv
import requests
from requests.exceptions import ConnectionError

def apps():
    """gets the app-ads.txt file and parses it for app data"""
    url = "https://appadstxt.bidswitch.com/apps.json"
    raw = requests.get(url, timeout=5.5)
    return raw.json()["apps"]

def urls():
    urls = []
    for obj in apps():
        devurl = obj["dev_url"]
        urls.append(devurl)
    return list(set(urls))


def urlcheck():
    """takes all devurls and checks their header return"""
    count = 10
    urlstatus = []
    for num, devurl in enumerate(urls()):
        appads = "https://" + devurl + "/app-ads.txt"
        try:
            x = requests.head(appads, timeout=3.5)
        except requests.exceptions.Timeout:
            status = "Timeout"
        except ConnectionError:
            status = "404"
        else:
            status = x.status_code
        tt = '"{}", "{}"'.format(appads, status)
        urlstatus.append(tt)
        count += 1
        if (num + 1) % 5 == 0:
            break
    return urlstatus

# def statuscsv():
#     """write the output to this csv file"""
#     with open("app-ads-txt.csv", "w") as outfile:
#         for i in urlcheck():
#             outfile.write(i)
#             outfile.write("\n")
#         return(outfile)

print(urlcheck())
# print(statuscsv())

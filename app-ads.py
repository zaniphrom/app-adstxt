#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import csv
import requests
from requests.exceptions import ConnectionError


# what i need is for all devurls that we have crawled and show that there is an ads.txt
# file present
# (which should be in here https://appadstxt.bidswitch.com/apps.json)
# list the bundleid and devurl
# and output to a csvfile


def apps():
    """gets the app-ads.txt file and parses it for app data"""
    url = "https://appadstxt.bidswitch.com/apps.json"
    raw = requests.get(url, timeout=5.5)
    return raw.json()["apps"]

def urls():
    urls = []
    for obj in apps():
        devurl = obj["dev_url"]
        if "google_play" in obj:
            gplay = obj["google_play"]["bundle"]
        else:
            gplay = "None"
        if "iTunes" in obj:
            itunes = obj["iTunes"]["bundle"]
        else:
            itunes = "None"
        tp = (devurl, gplay, itunes)
        urls.append(tp)
    return list(set(urls))

def urlcheck():
    """takes all devurls and checks their header return"""
    count = 0
    urlstatus = []
    for num, devurl in enumerate(urls()):
        appads = "https://" + devurl[0] + "/app-ads.txt"
        try:
            x = requests.head(appads, timeout=3.5)
        except requests.exceptions.Timeout:
            status = "Timeout"
        except ConnectionError:
            status = "404"
        else:
            status = x.status_code
        # tt = '"{}", "{}", "{}", "{}"'.format(appads, devurl[1], devurl[2], status)
        tt = (appads, devurl[1], devurl[2], status)
        # print(count, tt)
        urlstatus.append(tt)
        count += 1
        if (num + 1) % 10 == 0: # This line limits it to 10
            break
    return urlstatus

def bundle_key():
    """Swap the order to sort by bundle rather than dev URL"""
    bundle_ordering = []
    for tps in urlcheck():
        google_reorder = (tps[1], tps[0], tps[3])
        apple_reorder = (tps[2], tps[0], tps[3])
        if google_reorder[0] != "None":
            bundle_ordering.append(google_reorder)
        if apple_reorder[0] != "None":
            bundle_ordering.append(apple_reorder)
    return(bundle_ordering)

def statuscsv():
    """write the output to this csv file"""
    with open("app-ads-txt.csv", "w", encoding='utf-8') as outfile:
        for i in bundle_key():
            outfile.write(str(i)[1:-1])
            outfile.write("\n")
        return(outfile)

print(bundle_key())
# print(statuscsv())

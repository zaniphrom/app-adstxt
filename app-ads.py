#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import csv
import os.path
import requests
from requests.exceptions import ConnectionError


def apps():
    """gets the app-ads.txt file and parses it for app data"""
    # You need to copy this file into the directory from which you run this script
    # https://appadstxt.bidswitch.com/apps.json
    jsonfile = open("apps.json", "r")
    apps = json.load(jsonfile)["apps"]
    return apps


def get_token_json():
    """Get your toke from a local file"""
    f = open("token.json", "r")
    token = json.load(f)["slicer"]
    return str(token).rstrip("\n")


def ssp():
    ssp = "inneractive"
    return ssp


def append_details():
    """Add these details to the query for slicer instance, limit, and auth"""
    details = {
        "slicer_name": "traffic",
        "project_name": "bidswitch",
        "token": get_token_json(),
        "limit": 10,
    }
    return details


query = {
    "data_fields": ["imps", "dsp_final_price_adj_usd", "ads_txt_unknown"],
    "end_date": "-1d",
    "filters": [
        {
            "case_insensitive": True,
            "match": "equals",
            "name": "ssp",
            "search_mappings": True,
            "value": ["inneractive"],
        },
        {
            "case_insensitive": True,
            "match": "equals",
            "name": "inventory_type",
            "search_mappings": True,
            "value": ["application"],
        },
    ],
    "include_mappings": 1,
    "need_others": 1,
    "order_by": {"direction": "DESC", "name": "imps"},
    "split_by": ["referrer_domain"],
    "start_date": "-7d",
}


def build_query():
    """Build the query to post to slicer. This appends the 2nd object to the 1st"""
    cojoined_query = {**query, **append_details()}
    return cojoined_query


def slicer():
    slicer = "https://uslicer.iponweb.com/API/v2/query"
    return slicer


def top_bundles():
    get_info = requests.post(slicer(), json=build_query())
    raw = get_info.json()
    return json.dumps(raw, sort_keys=True, indent=4)


def extract_bundles():
    """Extract the bundle names from the top_bundles return"""
    bundle_names = []
    data = json.loads(top_bundles())["rows"]
    for obj in data:
        name = obj["name"]
        bundle_names.append(name)
    return bundle_names


def urls():
    """Parse the list of apps+dev_urls and arrange in a list of tuples"""
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


def get_bundle_dev_url():
    """From the list of tuples, fine the entries which match the bundles to check"""
    matches = []
    for bundle in extract_bundles():
        for tps in urls():
            iapps = tps[2]
            gapps = tps[1]
            # print(iapps)
            if bundle == iapps:
                pair = (bundle, tps[0])
                matches.append(pair)
            elif bundle == gapps:
                pair = (bundle, tps[0])
                matches.append(pair)
            else:
                continue
    return list(set(matches))


def urlcheck():
    """takes all devurls and checks their header return"""
    urlstatus = []
    for elem in get_bundle_dev_url():
        appads = "https://" + elem[1] + "/app-ads.txt"
        try:
            x = requests.head(appads, timeout=3.5, allow_redirects=True)
        except requests.exceptions.Timeout:
            status = "Timeout"
        except ConnectionError:
            status = "404"
        else:
            status = x.status_code
        tt = (elem[0], appads, status)
        print(tt)
        urlstatus.append(tt)
    return urlstatus


def statuscsv():
    """writes the output to this csv file"""
    filename = "app-ads-txt_" + ssp() + ".csv"
    with open(filename, "w", encoding="utf-8") as outfile:
        for i in urlcheck():
            print(i)
            outfile.write(str(i)[1:-1])
            outfile.write("\n")
        return outfile


if __name__ == "__main__":
    statuscsv()

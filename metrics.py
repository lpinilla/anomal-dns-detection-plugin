import requests
import json
import datetime
import dateutil
import numpy as np
import math
import re
import tldextract
import binascii
import csv

from collections import Counter
from flare.data_science.features import entropy
from flare.data_science.features import dga_classifier
from geoip import geolite2 #https://pythonhosted.org/python-geoip/
from base64 import b64encode, b64decode, b32decode
from utils import is_ip, domain_extract, domain_tld_extract, alexa_1m_rating

#Requests
http_cache = {}

#Feature N°2, geolocation from ip
def geo_from_ip(ip):
    return geolite2.lookup(ip)

#Feature N°4, quantity of numbers in hostname
def numbers_in_hostname(hostname):
    return sum(h.isnumeric() for h in hostname)

def entropy(s):
    p, lns = Counter(s), float(len(s))
    return round(-sum(count / lns * math.log2(count / lns) for count in list(p.values())), 2)

#Feature N°8: Consultas vacías (query name)
def empty_query_name(name):
    return name == None or name == ''

def zulu_timestamp_hour(timestamp):
    return datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ').hour

def zulu_timestamp_minutes(timestamp):
    return datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ').minutes

def hostname_entropy(hostname):
    return entropy(hostname)

# b32 decode hostname and calculate entropy
def hostname_b32_entropy(hostname):
    return entropy(b32decode(hostname))

# b64 decode hostname and calculate entropy
def hostname_b64_entropy(hostname):
    return entropy(b64decode(hostname))

#dga prediction of hostname, we use flare
def dga_classify(hostname):
    dga_c = dga_classifier()
    return dga_c.predict(hostname)

# auxiliary functions extracted from Flare framework
#https://github.com/austin-taylor/flare

def levenshtein(source, target):
    # Source
    # https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
    if len(source) < len(target):
        return levenshtein(target, source)
    # So now we have len(source) >= len(target).
    if len(target) == 0:
        return len(source)
    # We call tuple() to force strings to be used as sequences
    # ('c', 'a', 't', 's') - numpy uses them as values by default.
    source = np.array(tuple(source))
    target = np.array(tuple(target))
    # We use a dynamic programming algorithm, but with the
    # added optimization that we only need the last two rows
    # of the matrix.
    previous_row = np.arange(target.size + 1)
    for s in source:
        # Insertion (target grows longer than source):
        current_row = previous_row + 1
        # Substitution or matching:
        # Target and source items are aligned, and either
        # are different (cost of 1), or are the same (cost of 0).
        current_row[1:] = np.minimum(
            current_row[1:],
            np.add(previous_row[:-1], target != s))
        # Deletion (target grows shorter than source):
        current_row[1:] = np.minimum(
            current_row[1:],
            current_row[0:-1] + 1)
        previous_row = current_row
    return previous_row[-1]


#Aggregation flags, they return a df containing suspects
def beaconing_detector(df, params):
    message = 'Given a throttle value of %d, %d ips where flagged as having a beaconing behavior'
    client_ip = params['client_ip']
    timestamp = params['timestamp']
    threshold = params['threshold']
    time_diffs = build_time_differences(df, client_ip, timestamp)
    suspects_ips = time_diffs_suspects(time_diffs, threshold)
    sus_df = df[df[client_ip].isin(suspects_ips)]
    return sus_df, message % (threshold, len(suspects_ips))

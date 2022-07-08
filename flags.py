import requests
import numpy as np
import datetime
import dateutil
from base64 import b64encode, b64decode
from collections import Counter

#Feature N°13: Ver si hay un server que atienda http o https en la pag
def http_or_https_server(status, url):
    if status != 'OK' : return 0
    # Add http if its not on url
    if url == '':
        return 0
    http = None
    https = None
    if url[0:4] != 'http':
        http  = 'http://' + url
        https = 'https://' + url
    #it came with http or https
    else:
        if url[4] == 's':
            https = url
            # create http
            http = 'http' + url[5:]
        else:
            http = url
            http = 'https' + url[5:]
        #create https
    try:
        r1_status_code = requests.get(http).status_code
    except Exception as e:
        r1_status_code == -1
    try:
        r2_status_code = requests.get(https).status_code
    except Exception as e:
        r2_status_code = -1
    if r1_status_code == 200 or r2_status_code == 200:
        return 1
    return 0

def http_and_https_server(err_code, url):
    if err_code != 'NOERROR' : return 0
    # Add http if its not on url
    if url == '':
        return 0
    http = None
    https = None
    if url[0:4] != 'http':
        http  = 'http://' + url
        https = 'https://' + url
    #it came with http or https
    else:
        if url[4] == 's':
            https = url
            # create http
            http = 'http' + url[5:]
        else:
            http = url
            http = 'https' + url[5:]
        #create https
    r1 = requests.get(http)
    r2 = requests.get(https)
    if r1.status_code == 200 and r2.status_code == 200:
        return 1
    return 0

#https://stackoverflow.com/questions/8571501/how-to-check-whether-a-string-is-base64-encoded-or-not#:~:text=In%20base64%20encoding%2C%20the%20character,0%20or%20more%20base64%20groups.
def has_dns_data_b64_encoded(dns_data):
    if dns_data is None or dns_data == '' : return False
    if dns_data[0] == '[': #list
        dns_data = dns_data[1:-1].split(';')
        for i in range(len(dns_data)):
            dns_data[i] = dns_data[i][1:-1]
    for resp in dns_data:
        if resp == '': continue
        try:
            if b64encode(b64decode(resp)).decode('ascii') == resp:
                return True
        except:
            continue
    return False

def date_time_difference(arr):
    return np.array([(dateutil.parser.isoparse(arr[i+1])-dateutil.parser.isoparse(arr[i])).seconds for i in range(round(len(arr)/2))])

def build_time_differences(df, client_ip_name, timestamp_name):
    gb = df.groupby(client_ip_name)[timestamp_name]
    return [{'client': key, 'diffs': date_time_difference(g.values)} for key,g in gb]

def time_diffs_suspects(time_diffs, throttle):
    suspects = []
    for t in time_diffs:
        if len(t['diffs']) != 0:
            ones_rate = Counter(list(Counter(t['diffs']).values()))[1] / len(t['diffs'])
            if ones_rate < throttle:
                suspects.append(t)
    return [x['client'] for x in suspects]

#Aggregation flags, they return a df containing suspects
def beaconing_detector(df, params):
    message = 'Given a throttle value of %.2f, %d ips where flagged as having a beaconing behavior'
    client_ip = params['client_ip']
    timestamp = params['timestamp']
    threshold = params['threshold']
    time_diffs = build_time_differences(df, client_ip, timestamp)
    suspects_ips = time_diffs_suspects(time_diffs, threshold)
    sus_df = df[df[client_ip].isin(suspects_ips)]
    return sus_df, message % (threshold, len(suspects_ips))

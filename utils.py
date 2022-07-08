import csv
import re
import tldextract
import numpy as np
from pathlib import Path

def is_ip(address):
    # Used to validate if string is an ipaddress
    ip = re.match(
        '^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', address)
    if ip:
        return True
    else:
        return False

def domain_extract(uri):
    # Extracts domain, ex: www.google.com would return google
    try:
        ext = tldextract.extract(uri)
        if (not ext.suffix):
            return np.nan
        else:
            return ext.domain
    except Exception:
        return ''


def domain_tld_extract(domain):
    # Extracts domain and TLD. subdomain.sub.google.com returns google.com
    t = domain.split('.')
    ip_check = is_ip(domain)
    if ip_check:
        return domain
    try:
        ext = tldextract.extract(domain)
        if ext.suffix:
            return '{}.{}'.format(ext.domain, ext.suffix)
        return domain
    except Exception:
        return ''

#Alexa
alexa_initialized = False
alexa = {}

def init_alexa():
    global alexa_initialized
    if not alexa_initialized:
        alexa_initialized = True
        here = Path(__file__).parent
        file_path = here / 'top-1m.csv'
        with open(file_path, 'r') as f:
            try:
                reader = csv.reader(f)
            except:
                exit('Alexa init failed, could not open file')
            index = 0
            for r in reader:
                alexa[r[0]] = index
                index += 1

def alexa_1m_rating(url):
    init_alexa()
    tld = domain_tld_extract(url)
    if tld not in alexa:
        return 9_999_999
    return alexa[tld]

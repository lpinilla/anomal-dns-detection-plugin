from utils import domain_tld_extract, alexa_1m_rating

def remove_status_error(data):
    return data == 'Error'

def remove_match(field, params):
    return field == params['keyword']

def remove_tld(hostnames, params):
    return domain_tld_extract(hostnames) == params['whitelisted']

def remove_alexa_1m(hostnames):
    return alexa_1m_rating(hostnames)

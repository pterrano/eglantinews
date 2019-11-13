import requests


def send_soap(path, urn, service, body):
    soap = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
    soap += '<s:Body>'
    soap += '<u:{service} xmlns:u="{urn}">{body}</u:{service}>'
    soap += '</s:Body>'
    soap += '</s:Envelope>'
    soap = soap.format(urn=urn, service=service, body=body)

    headers = {
        'content-type': 'text/xml;charset="utf-8"',
        'soapaction': '{urn}#{service}'
    }

    result = requests.post('http://tv:7676/%s' % path, data=soap, headers=headers)

    print(result.text)




#_source_names = send_soap('rcr', 'urn:samsung.com:service:MainTVAgent2:1', 'GetSourceList', '')

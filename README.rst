=================
unikold.connector
=================

Plone-Addon for making SOAP-Requests.
Requests are automatically stored as `SOAPQuery` objects which allows caching of the responses.

You could see this addon as extensible wrapper for [zeep](https://pypi.org/project/zeep/).


Features
--------

- SOAP-Requests are cached (lifetime can be specified)
- Live-View to test your SOAP-Requests: `soap_test`


Examples
--------

After installing this addon you can make SOAP-Requests like this:

```
soapConnector = SOAPConnector(
    'http://webservices.daehosting.com/services/isbnservice.wso?WSDL',  # URL to WSDL file
    'IsValidISBN13',                                                    # name of the method
    '9783492700764',                                                    # method parameter
    24                                                                  # lifetime of this request in hours
)
response = soapConnector.get()
```

If the request already exists and its lifetime did not expire `soapConnector` simply returns the stored response.
If the request exists but is outdated it will be updated before returning the response.
If the request does not yet exist a new object will be created.

To get the corresponding query object:

```
queryObject = soapConnector.getQuery()
```

Above example without this addon would look like this (remember no caching):

```
from zeep import Client
url = 'http://webservices.daehosting.com/services/isbnservice.wso?WSDL'
client = Client(url)
print client.service.IsValidISBN13('9783492700764')
```


Installation
------------

Install unikold.connector by adding it to your buildout::

    [buildout]

    ...

    eggs =
        unikold.connector


and then running ``bin/buildout``



License
-------

The project is licensed under the GPLv2.

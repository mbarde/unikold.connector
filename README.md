unikold.connector
=================

Plone-Addon for making persistent SOAP-Requests using a fast and modern Python SOAP client: [zeep](https://pypi.org/project/zeep/).

Requests are automatically stored as `SOAPQuery` objects which allows caching with variable lifetime of the responses.


Features
--------

- SOAP-Requests are cached (lifetime can be specified)
- Live-View to test your SOAP-Requests: `soap_test`


Examples
--------

After installing this addon you can make SOAP-Requests like this:

```python
from unikold.connector.soap import SOAPConnector
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
If the request does not yet exist a new object will be created. Its path will be `{SOAP-Queries-Folder}.{WSDL-URL}.{Methodname}.{Parameter}` (where `{SOAP-Queries-Folder}` has to be specified in the controlpanel of this addon - otherwise a folder will be created at your sites' root).

To get the corresponding query object:

```python
queryObject = soapConnector.getQuery()
```

Above example without this addon would look like this (remember no persistent objects, no caching):

```python
from zeep import Client
url = 'http://webservices.daehosting.com/services/isbnservice.wso?WSDL'
client = Client(url)
response = client.service.IsValidISBN13('9783492700764')
```


Installation
------------

Install unikold.connector by adding it to your buildout::

    [buildout]

    ...

    eggs =
        unikold.connector


and then running ``bin/buildout``


Testing
------------

Before you can run the tests you need to create a file called `config.py` in the `tests` folder,
containing following constants:

```python
# -*- coding: utf-8 -*-
soap_test_url = u'http://webservices.daehosting.com/services/isbnservice.wso?WSDL'
soap_test_method = u'IsValidISBN13'
soap_test_method_parameter = u'9783492700764'

# config data needed for LSF tests
lsf_wsdl_url = u''  # URL to LSF WSDL file containing getDataXML method
lsf_test_object_type = u''  # LSF object type
lsf_test_conditions = []  # a list of tuples, i.e. [('prename', 'Peter')]
lsf_wsdl_search_url = u''  #  URL to LSF search WSDL
lsf_search_test_method_parameter = u''  # XML-formatted parameter for the search method
lsf_auth_username = u''
lsf_auth_password = u''
```

* `bin/test`
* `bin/code-analysis`

TypeError: string indices must be integers
------------

Make sure this fix has been applied to zeep: https://github.com/mvantellingen/python-zeep/pull/657/commits/a2b7ec0296bcb0ac47a5d15669dcb769447820eb


License
-------

The project is licensed under the GPLv2.

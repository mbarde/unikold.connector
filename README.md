unikold.connector
=================

Plone-Addon for making persistent SOAP requests using a fast and modern Python SOAP client: [zeep](https://pypi.org/project/zeep/).

Requests are automatically stored as `SOAPQuery` objects which allows caching with variable lifetime of the responses.


Features
--------

- SOAP requests are cached (lifetime can be specified)
- Live-View to test your SOAP requests: `test_soap`: [https://raw.githubusercontent.com/mbarde/unikold.connector/master/docs/connector.gif](https://raw.githubusercontent.com/mbarde/unikold.connector/master/docs/connector.gif)
- Specific queries (`LSFQuery`, `LSFSearchQuery`) to easily connect to products of [HIS eG](https://www.his.de) via their SOAP API (`dbinterface`)
- Plain XML requests (also supports basic authentication)

Installation
--------
1. Add `unikold.connector` to your buildout
2. Install via `prefs_install_products_form`
3. Create a `SOAPQueriesFolder`
* For security reasons `SOAPQueriesFolder` are not globally addable by default - to be able to add it you need to allow adding this content type at the desired location temporarily
* In this folder all queries will be stored
* Maybe you also want to exclude it from navigation
4. Set path to this folder in `@@unikold-connector-controlpanel`
5. If you want to make use of LSF-Queries you also have to define settings in `@@unikold-connector-lsf-controlpanel`


Examples
--------

After installing this addon you can make SOAP requests like this:

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
If the request does not yet exist, a new object will be created. Its path will be `{SOAP-Queries-Folder}.{WSDL-URL}.{Methodname}.{Parameter}` (where `{SOAP-Queries-Folder}` has to be specified in the controlpanel of this addon - otherwise a folder will be created at your sites' root).

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

Make a XML request (which will be cached 24 hours):

```python
from unikold.connector.xml import XMLConnector
xmlConnector = XMLConnector(
    'https://www.w3schools.com/xml/note.xml',
    24,
    queryParams=['prename=Peter', 'surname=Lustig'],  # query parameters (optional)
    basicAuthCredentials=('username', 'password')  # credentials for basic authentication (optional)
)
xmlData = xmlConnector.get()
# xmlData is a lxml.etree object:
print(etree.tostring(xmlData))
```

Automate updating of queries
--------

Use Zope clock server to call `unikold.connector.update` (user must have permission `cmf.ManagePortal`):

```
[client2]
zope-conf-additional =
    <clock-server>
       method /SiteName/unikold.connector.update
       period 2880
       user username
       password *****
       host hostname.com
    </clock-server>
```

Parameters explained in detail here: https://docs.plone.org/develop/plone/misc/asyncronoustasks.html#clock-server

Updating big amounts of queries can take a while so its advisable to run the task on a dedicated client.


Testing
------------

Before you can run the tests you need to create a file called `config.py` in the `tests` folder,
containing following constants:

```python
# -*- coding: utf-8 -*-
soap_test_url = u'http://webservices.daehosting.com/services/isbnservice.wso?WSDL'
soap_test_method = u'IsValidISBN13'
soap_test_method_parameter = u'9783492700764'

xml_test_url = u'https://www.w3schools.com/xml/note.xml

# config data required for XML tests with basic authentication
xml_basic_auth_url = u''
xml_basic_auth_username = u''
xml_basic_auth_password = u''

# config data required for LSF tests
lsf_wsdl_url = u''  # URL to LSF WSDL file containing getDataXML method
lsf_test_object_type = u''  # LSF object type
lsf_test_conditions = []  # a list of tuples, i.e. [('prename', 'Peter')]
lsf_wsdl_search_url = u''  #  URL to LSF search WSDL
lsf_search_test_method_parameter = u''  # XML-formatted parameter for the search method

# for testing LSF methods with authentication
lsf_auth_username = u''
lsf_auth_password = u''
lsf_auth_test_object_type = u''  # LSF object type
lsf_auth_test_conditions_0 = []  # a list of tuples, i.e. [('prename', 'Peter')]
lsf_auth_test_conditions_1 = []  # a list of tuples, i.e. [('prename', 'Peter')]
```

* `bin/test`
* `bin/code-analysis`

TypeError: string indices must be integers
------------

Make sure this fix has been applied to zeep: https://github.com/mvantellingen/python-zeep/pull/657/commits/a2b7ec0296bcb0ac47a5d15669dcb769447820eb


License
-------

The project is licensed under the GPLv2.

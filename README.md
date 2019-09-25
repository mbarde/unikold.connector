

unikold.connector
=================

Plone-Addon for making cachable queries to API endpoints supporting following protocols:

- Plain XML
- SOAP (using a fast and modern Python SOAP client: [zeep](https://pypi.org/project/zeep/))
- LDAP

Can be easily extended.


Features
--------

- SOAP requests are cached (lifetime can be specified)
- Live-View to test your SOAP requests: `test_soap`: [https://raw.githubusercontent.com/mbarde/unikold.connector/master/docs/connector.gif](https://raw.githubusercontent.com/mbarde/unikold.connector/master/docs/connector.gif)
- Specific queries (`LSFQuery`, `LSFSearchQuery`) to easily connect to products of [HIS eG](https://www.his.de) via their SOAP API (`dbinterface`)
- Plain XML requests (also supports basic authentication)
- LDAP search queries

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
6. If you want to make use of LDAP-Queries you also have to define settings in `@@unikold-connector-ldap-controlpanel`


Examples
--------

### Soap Requests

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

### XML Requests

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

### LDAP Requests

```python
from unikold.connector.ldap import LDAPSearchConnector
searchFilter = 'mail=mbarde@uni-koblenz.de'
ldapConnector = LDAPSearchConnector(searchFilter=searchFilter)
resultList = ldapConnector.get()
```

This example only works if you set the LDAP default options in `@@unikold-connector-ldap-controlpanel`.

If you did not set defaults or want to use different values for these options you can also set them explicitly for each query:

```python
from unikold.connector.ldap import LDAPSearchConnector
searchFilter = 'mail=mbarde@uni-koblenz.de'
ldapConnector = LDAPSearchConnector(
    address='ldap://[...]', port=389, baseDN='dc=[...]',
    searchFilter=searchFilter, username='uid=[...]', password='****',
    queryLifetimeInHours=24, excludeFromAutoUpdate=True
)
resultList = ldapConnector.get()
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

To create a query which should be excluded from automatic updates you have to pass `excludeFromAutoUpdate=True` to the corresponding connector.


Testing
------------

Before you can run the tests you need to create a file called `config.py` in the `tests` folder,
containing following constants:

```python
# -*- coding: utf-8 -*-
soap_test_url = u'http://webservices.daehosting.com/services/isbnservice.wso?WSDL'
soap_test_method = u'IsValidISBN13'
soap_test_method_parameter = u'9783492700764'

xml_test_url = u'https://en.wikipedia.org/w/api.php?format=xml&action=query&prop=extracts&exintro&explaintext&redirects=1&titles=Rick_and_Morty'

# config data needed for XML auth tests
xml_basic_auth_url = u''
xml_basic_auth_username = u''
xml_basic_auth_password = u''

# config data needed for LSF tests
lsf_wsdl_url = u'[...]/qisserver/services/dbinterface?WSDL'
lsf_test_object_type = u''  # LSF object type
lsf_test_conditions = []
lsf_auth_test_object_type = u''
lsf_auth_test_conditions = []
lsf_wsdl_search_url = u'[...]/qisserver/services/soapsearch?WSDL'
lsf_search_test_method_parameter = u''
lsf_auth_username = u''
lsf_auth_password = u''

# config data needed for LDAP tests
ldap_server_address = u'ldap://[...]'
ldap_server_port = 389
ldap_server_base_dn = u''
ldap_search_username = u''
ldap_search_password = u''

```

* `bin/test`
* `bin/code-analysis`

TypeError: string indices must be integers
------------

Make sure this fix has been applied to zeep: https://github.com/mvantellingen/python-zeep/pull/657/commits/a2b7ec0296bcb0ac47a5d15669dcb769447820eb


License
-------

The project is licensed under the GPLv2.

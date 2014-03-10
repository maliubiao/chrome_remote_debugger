chrome-remote-debugger
======================

###enable debugging
```shell 
google-chrome --remote-debugging-port=9222
```
###Demo
```shell
In [1]: from chrome_debugger import interface

In [2]: interface.get_app_list("localhost:9222")
Out[2]: 
[{u'description': u'',
  u'devtoolsFrontendUrl': u'/devtools/devtools.html?ws=localhost:9222/devtools/page/0B4138C2-9713-B2C2-EED0-B00755867E95',
  u'id': u'0B4138C2-9713-B2C2-EED0-B00755867E95',
  u'title': u'\u6253\u5f00\u65b0\u7684\u6807\u7b7e\u9875',
  u'type': u'page',
  u'url': u'chrome://newtab/',
  u'webSocketDebuggerUrl': u'ws://localhost:9222/devtools/page/0B4138C2-9713-B2C2-EED0-B00755867E95'},
 {u'description': u'',
  u'devtoolsFrontendUrl': u'/devtools/devtools.html?ws=localhost:9222/devtools/page/FBA82744-6572-C5B4-2702-E45CA517A230',
  u'faviconUrl': u'http://www.opensuse.org/favicon.ico',
  u'id': u'FBA82744-6572-C5B4-2702-E45CA517A230',
  u'title': u'openSUSE.org',
  u'type': u'page',
  u'url': u'http://www.opensuse.org/en/',
  u'webSocketDebuggerUrl': u'ws://localhost:9222/devtools/page/FBA82744-6572-C5B4-2702-E45CA517A230'},
  ...

```

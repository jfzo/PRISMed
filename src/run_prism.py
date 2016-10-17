# -*- coding: utf-8 -*-

from prism_controller import FrontController
import bottle
import logging

host_address = '127.0.0.1'
root = FrontController(webpath='/prism')

root.addprotocol('soap',
        tns='http://example.com/demo',
        typenamespace='http://example.com/demo/types',
        baseURL='http://'+host_address+':8080/prism/',
)

root.addprotocol('restjson')

bottle.mount('/prism/', root.wsgiapp())

logging.basicConfig(level=logging.DEBUG)
#bottle.run()
bottle.run(host=host_address, port=8080)
# -*- coding: utf-8 -*-

from prism_controller import FrontController
import bottle
import logging
import prism_config as config


logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='/tmp/prism.log',level=logging.DEBUG)


root = FrontController(webpath='/prism')

root.addprotocol('soap',
        tns='http://example.com/demo',
        typenamespace='http://example.com/demo/types',
        baseURL='http://'+config.bind_address+':'+str(config.bind_port)+'/prism/',
)

root.addprotocol('restjson')

bottle.mount('/prism/', root.wsgiapp())

logging.basicConfig(level=logging.DEBUG)
#bottle.run()
logging.info("PRISM Starting...")
bottle.run(host=config.bind_address, port=config.bind_port)

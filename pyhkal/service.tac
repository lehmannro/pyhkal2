#!/usr/bin/env python
from twisted.application import service
import pyhkal.engine

application = service.Application("PyHKAL")
pyhkal.engine.run(application)

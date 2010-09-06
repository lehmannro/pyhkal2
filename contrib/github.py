from twisted.internet import reactor, protocol
from twisted.web import http
import time

DEFAULT_TIMEOUT = 5

__settings__ = dict(
    postreceive=dict(
        port="TCP port to listen for Post-receive notifications",
        timeout="""Number of seconds to elapse during two pulls.
            Defaults to %d.""" % DEFAULT_TIMEOUT,
    ),
)


class PostReceiveHook(protocol.ServerFactory):
    #XXX is this really required? LineOnlyReceiver might suffice
    protocol = http.HTTPChannel
    def __init__(self, timeout):
        self.last_update = 0
        self.timeout = timeout
    def buildProtocol(self, addr):
        now = time.time()
        if now - self.last_update > self.timeout: # primitive DoS prevention
            self.last_update = now
            # Note: this does not inherit *any* environment
            reactor.spawnProcess(GitPull(), 'git', args=['git', 'pull'])
        return protocol.ServerFactory.buildProtocol(self, addr)

class GitPull(protocol.ProcessProtocol):
    #XXX error/success reporting
    pass

@hook('startup')
def listen():
    hook = PostReceiveHook(remember('postreceive timeout', DEFAULT_TIMEOUT))
    twist(remember('postreceive port'), hook)

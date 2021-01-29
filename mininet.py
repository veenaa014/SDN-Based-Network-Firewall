from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

class MultiSwitchTopo(Topo):
    def build(self, n=4):
        switch = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        self.addLink(switch,switch2)
        # Python's range(N) generates 0..N-1
        for h in range(n):
            host = self.addHost('h%s' % (h + 1))
            self.addLink(host, switch)
        
        for h in range(n):
            host = self.addHost('h%s' % (h + n + 1))
            self.addLink(host, switch)

def simpleTest():
    "Create and test a simple network"
    topo = MultiSwitchTopo(n=4)
    net = Mininet(topo)
    net.start()
    print ("Dumping host connections")
    dumpNodeConnections(net.hosts)
    print ("Testing network connectivity")
    net.pingAll()
    net.stop()


topos = { 'MultiSwitchTopo': ( lambda: MultiSwitchTopo() ) }

if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    simpleTest()

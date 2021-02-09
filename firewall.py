from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str, str_to_dpid
from pox.lib.util import str_to_bool, dpid_to_str
import time
import pox.lib.packet as pkt
from pymongo import MongoClient
import datetime

log = core.getLogger()

class FirewallSwitch (object):
  def __init__ (self, connection):
    self.connection = connection
    connection.addListeners(self)

  
  def _handle_PacketIn (self, event):
    packet = event.parsed

    def iptostring(packet):
      return "Source IP: " + str(packet.srcip) + ", Destination IP: " + str(packet.dstip)
    def logdb(db, ip, event, msg):
      log.info("Event " + event + ", msg " + msg)
      db.insert_one({"time": datetime.datetime.utcnow(), "event": event, "source": str(ip.srcip), "destination": str(ip.dstip),
      "message": msg, "switch": dpid_to_str(self.connection.dpid)})

    ip = packet.find('ipv4')
    if ip is not None:
      client = MongoClient('localhost', 27017)
      col = client.pox.rules
      logmongo = client.pox.log
      tcp = packet.find("tcp")
      udp = packet.find("udp")
      icmp = packet.find("icmp")
      for rule in col.find():
        source = rule['source']
        des = rule['destination']
        if source != "*" and source != str(ip.srcip):
          continue
        if des != "*" and des != str(ip.dstip):
          continue

        protocol = rule['protocol']
        if protocol == "icmp" and icmp is not None:
          logdb(logmongo, ip, "Deny", "ICMP packet broke rule, dropping packet")
          return
        if protocol == "tcp" and tcp is not None:
          logdb(logmongo, ip, "Deny", "TCP packet broke rule, dropping packet")
          return
        if protocol == "udp" and udp is not None:
          logdb(logmongo, ip, "Deny", "UDP packet broke rule, dropping packet")
          return
      
      if tcp is not None:
        logdb(logmongo, ip, "Permit", "TCP packet permitted")
      if udp is not None:
        logdb(logmongo, ip, "Permit", "UDP packet permitted")
      if icmp is not None:
        logdb(logmongo, ip, "Permit", "ICMP packet permitted")

    msg = of.ofp_packet_out()
    msg.data = event.ofp
    action = of.ofp_action_output(port = of.OFPP_ALL)
    msg.actions.append(action)
    self.connection.send(msg)
    return


class firewall (object):
  def __init__ (self):
    core.openflow.addListeners(self)
  def _handle_ConnectionUp (self, event):
    log.info("Connection %s" % (event.connection,))
    FirewallSwitch(event.connection)


def launch ():
  core.registerNew(firewall)

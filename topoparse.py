#!/usr/bin/env python2

import re
import sys
import jsonpickle
import sys

class IBNode:
	def __init__(self):
		pass

class IBLink:
	def __init__(self):
		#The LID of the port on the first host
		self.host1_portlid = None
		#The port nr on the first host
		self.host1_port = None
		
		self.host2_portlid = None
		self.host2_port = None

		self.linktype = None


def parseTopologyfile(topofile):
	nodes = {}
	links = {}
	curswitch=None
	for line in topofile:
		if line.startswith('\n'):
			curswitch=None
			continue

		if line.startswith('Switch'):
			curswitch = IBNode()
			m=re.search('Switch\s+([0-9]+)\s+"([^"]+)"[^"]+"([^"]+)".*lid ([0-9]+)', line)
			curswitch.available_ports = m.group(1)
			curswitch.connected_ports = 0
			curswitch.guid = m.group(2).lstrip('S-')
			curswitch.name = m.group(3)
			curswitch.lid = m.group(4)
			curswitch.type = 'switch'

			nodes[curswitch.guid] = curswitch
			continue

		if line.startswith('[') and curswitch:
			curswitch.connected_ports+=1
			m=re.search('\[([0-9]+)\]\s*"([^"]+)"\[([0-9]+)\][^"]+"([^"]+)".*lid ([0-9]+) (.+)$', line)
			switchport=m.group(1)
			nodeguid=m.group(2)
			nodeport=m.group(3)
			nodename=m.group(4)
			#For a switch the LID is global, for a Ca it is per port
			portlid=m.group(5)
			linktype=m.group(6)

			if nodeguid.startswith('S-'):
				nodetype = 'switch'
				nodeguid=nodeguid.lstrip('S-')
			elif nodeguid.startswith('H-'):
				nodetype = 'HCA'
				nodeguid=nodeguid.lstrip('H-')
			else:
				print 'Unknown prefix for host guid: %s' % nodeguid
				print 'Should be "H-" or "S-"'
				sys.exit(1)

			try:
				node = nodes[nodeguid]
				if node.type != 'switch':
					node.connected_ports+=1
			except KeyError:
				node = IBNode()
				node.guid = nodeguid
				node.name = nodename
				node.type = nodetype
				node.connected_ports = 1
				nodes[nodeguid] = node

			if curswitch.guid < node.guid:
				host1=curswitch
				host2=node
			else:
				host1=node
				host2=curswitch

			#We add the current ports and LIDs (these are acutally valid only for
			#links not nodes)
			curswitch.port = switchport
			node.port = nodeport
			node.lid = portlid

			linkhash = "%s%s%s%s" % (host1.guid,host2.guid,host1.port,host2.port)
			try:
				link = links[linkhash]
			except KeyError:
				link = IBLink()
				link.host1_portlid = host1.lid
				link.host2_portlid = host2.lid
				link.host1_port = host1.port
				link.host2_port = host2.port
				link.host1_guid = host1.guid
				link.host2_guid = host2.guid
				links[linkhash] = link

			continue

		if line.startswith('Ca'):
			m=re.search('Ca\s+([0-9]+)\s+"([^"]+)"', line)
			portcount=m.group(1)
			nodeguid=m.group(2).lstrip('H-')
			node=nodes[nodeguid]
			node.available_ports=portcount

			# print switchport,nodeguid,nodeport,nodename,portlid,linktype
	return nodes, links

#This function is UT cluster specific and removes some clutter from
#the names of our nodes
def beautifyNames(nodes):
	for node in nodes:
		node.name = node.name.rstrip('mlx4_0')
		if node.type=='switch':
			node.name = node.name.replace('MF0;','')

if __name__=='__main__':
	if len(sys.argv) != 2:
		print "Please point to the output of ibnetdiscover:"
		print "  %s [ibnetdiscover_output]" % sys.argv[0]
		sys.exit(1)

	topofile = open(sys.argv[1], 'r')
	nodes, links = parseTopologyfile(topofile)
	topofile.close()
	print "Nodes parsed %d, connections parsed: %d" % (len(nodes),len(links))

	beautifyNames(nodes.values())

	outfile = open('%s.json' % sys.argv[1], 'w')
	outfile.write(jsonpickle.encode(
		{'nodes': nodes.values(), 'links':links.values()}, unpicklable=False))
	outfile.close()



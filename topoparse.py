#!/usr/bin/env python

import re
import sys
import jsonpickle

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
			m=re.search('[^"]+"([^"]+)"[^"]+"([^"]+)".*lid ([0-9]+)', line)
			curswitch.guid = m.group(1).lstrip('S-')
			curswitch.name = m.group(2)
			curswitch.lid = m.group(3)
			curswitch.type = 'S'

			print curswitch.name, curswitch.guid, curswitch.lid
			nodes[curswitch.guid] = curswitch
			continue

		if line.startswith('[') and curswitch:
			m=re.search('\[([0-9]+)\]\s*"([^"]+)"\[([0-9]+)\][^"]+"([^"]+)".*lid ([0-9]+) (.+)$', line)
			switchport=m.group(1)
			nodeguid=m.group(2)
			nodeport=m.group(3)
			nodename=m.group(4)
			#For a switch the LID is global, for a Ca it is per port
			portlid=m.group(5)
			linktype=m.group(6)

			if nodeguid.startswith('S-'):
				nodetype = 'S'
				nodeguid=nodeguid.lstrip('S-')
			elif nodeguid.startswith('H-'):
				nodetype = 'H'
				nodeguid=nodeguid.lstrip('H-')
			else:
				print 'Unknown prefix for host guid: %s' % nodeguid
				print 'Should be "H-" or "S-"'
				sys.exit(1)

			try:
				node = nodes[nodeguid]
			except KeyError:
				node = IBNode()
				node.guid = nodeguid
				node.name = nodename
				node.type = nodetype
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


			print switchport,nodeguid,nodeport,nodename,portlid,linktype
	return nodes, links


if __name__=='__main__':
	topofile = open('topo', 'r')
	nodes, links = parseTopologyfile(topofile)
	topofile.close()
	print len(nodes)
	print len(links)

	outfile = open('topo.json', 'w')
	outfile.write(jsonpickle.encode(
		{'nodes': nodes.values(), 'links':links.values()}, unpicklable=False))
	outfile.close()



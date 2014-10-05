#!/usr/bin/env python

import re

class IBNode:
	def __init__(self):
		pass


nodes = {}

if __name__=='__main__':
	topofile = open('topo', 'r')
	mode=''
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

			print curswitch.name, curswitch.guid, curswitch.lid
			nodes[curswitch.guid] = curswitch
			continue

		if line.startswith('[') and curswitch:
			m=re.search('\[([0-9]+)\]\s*"([^"]+)"\[([0-9]+)\][^"]+"([^"]+)".*lid ([0-9]+) (.+)$', line)
			switchport=m.group(1)
			nodeguid=m.group(2)
			nodeport=m.group(3)
			nodename=m.group(4)
			nodelid=m.group(5)
			link=m.group(6)
			print switchport,nodeguid,nodeport,nodename,nodelid,link




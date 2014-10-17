infiniband_topology
===================

A small web application to visualize an Infiniband fabric

It consists of two parts: a parser written in Python and a visualization application written in Javascript.

The parser:
- takes the output of the "ibnetdiscover" utility as it's input
- parses all the nodes and connections
- outputs this info into a .json file

The visualizer:
- loads the .json file
- displays the fabric topology using d3.js force layout
- allow you to interact with the visualization

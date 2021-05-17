#!/usr/bin/env python

'''Takes a gzip compress moses search graph and returns a gzip compress htk word graph.'''

import sys, gzip

__author__ = "Miguel Domingo"

def addEdge(origin, destiny, score, word):
  global new_nodes
  global edges
  if len(word.split()) > 1:
    words = word.split()
    for i in range(len(words)):
      if words[i] == '\\':
        words[i] = "backslash"
    new_nodes += 1
    edges.append([origin, new_nodes, 0.0, words[0]])
    for i in range(1, len(words) - 1):
      edges.append([new_nodes, new_nodes + 1, 0.0, words[i]])
      new_nodes += 1
    edges.append([new_nodes, destiny, score, words[-1]])
  elif word == '\\':
    edges.append([origin, destiny, score, "backslash"])
  else:
    edges.append([origin, destiny, score, word])

def outputWG():
  f = gzip.open(sys.argv[4], 'wb')
  f.write("VERSION=1.0\n" + "UTTERANCE=1\n" + "lmscale=0\n" + "wdpenalty=0\n" + "acscale=1\n")
  f.write("N=" + str(new_nodes + 2) + "\tL=" + str(len(edges)) + '\n')
  for i in range(new_nodes + 2): 
    f.write("I=" + str(i) + "\tt=0.0\n")
  f.write("J=" + "0" + "\tS=" + str(edges[-1][0]) + "\tE=" + str(edges[-1][1]) + "\ta=" + str(edges[-1][2]) + "\tl=1.0\tW=" + edges[-1][3] + '\n')
  j = 1
  for i in range(len(edges) - 1):
    e = edges[i]
    if e[1] == -9000 : continue
    f.write("J=" + str(j) + "\tS=" + str(e[0]) + "\tE=" + str(e[1]) + "\ta=" + str(e[2]) + "\tl=1.0\tW=" + e[3] + '\n')
    j += 1
  f.close()

def removeSinkNodes():
  visited = [0 for i in range(new_nodes + 1)]
  queued = []
  edge_list = {}
  for n in range(new_nodes + 1):
    edge_list[n] = []
  for e in edges:
    edge_list[e[1]].append(e[0])
  queued.append(new_nodes)
  while len(queued) > 0:
    current_node = queued.pop()
    if visited[current_node] == 0:
      visited[current_node] = 1
      for e in edge_list[current_node]:
        if visited[e] == 0:
          queued.append(e)
  for e in edges:
    if visited[e[1]] == 0:
      e[1] = -9000 # It's over 9000!

if len(sys.argv) < 5 or sys.argv[1] != "-i" or sys.argv[3] != "-o":
  sys.stderr.write("Usage: " + sys.argv[0] + " -i input_file -o output_file\n")
  sys.exit(-1)

if __name__ == "__main__":

  max_node = 0
  for line in gzip.open(sys.argv[2], 'rb'):
    node = int(line.split("hyp=")[1].split()[0])
    if node > max_node:
      max_node = node

  final_nodes = [0 for i in range(max_node + 1)]
  new_nodes = max_node
  edges = []

  for line in gzip.open(sys.argv[2], 'rb'):
    edge = line.strip()
    if len(edge.split()) > 3:
      addEdge(int(edge.split("back=")[1].split()[0]), int(edge.split("hyp=")[1].split()[0]), float(edge.split("transition=")[1].split()[0]), edge.split("out=")[1])
      if int(edge.split("forward=")[1].split()[0]) == -1:
        final_nodes[int(edge.split("hyp=")[1].split()[0])] = 1
      if len(edge.split("recombined=")) > 1:
        addEdge(int(edge.split("hyp=")[1].split()[0]), int(edge.split("recombined=")[1].split()[0]), 0.0, "!NULL")

  new_nodes += 1
  for node in range(max_node + 1):
    if final_nodes[node] == 1:
      addEdge(node, new_nodes, 0.0, "!NULL")
  removeSinkNodes()
  addEdge(new_nodes, new_nodes + 2, 0.0, "</s>")
  new_nodes += 1
  addEdge(new_nodes, 0, 0.0, "<s>")

  outputWG()

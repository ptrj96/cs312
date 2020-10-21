#!/usr/bin/python3


from CS312Graph import *
import time
from ArrayQueue import *
from HeapQueue import *


class NetworkRoutingSolver:
    def __init__( self):
        pass

    def initializeNetwork( self, network ):
        assert( type(network) == CS312Graph )
        self.network = network

    def getShortestPath( self, destIndex ):
        self.dest = destIndex
        # TODO: RETURN THE SHORTEST PATH FOR destIndex
        #       INSTEAD OF THE DUMMY SET OF EDGES BELOW
        #       IT'S JUST AN EXAMPLE OF THE FORMAT YOU'LL 
        #       NEED TO USE
        path_edges = []
        path_ids = []
        total_length = 0
        nodes = self.network.getNodes()
        src_node = nodes[self.source]
        dest_node = nodes[self.dest]
        cur_node = nodes[self.dest]
        while cur_node != src_node:
            path_ids.append(cur_node.node_id)
            cur_node = nodes[self.prev[cur_node.node_id].node_id]
        path_ids.append(self.source)
        cur_node = nodes[self.source]
        path_ids.reverse()
        for i in range(len(path_ids)-1):
            start_node = nodes[path_ids[i]]
            path_node = nodes[path_ids[i+1]]
            for edge in start_node.neighbors:
                if edge.dest.node_id == path_node.node_id:
                    path_edges.append((start_node.loc, edge.dest.loc, '{:.0f}'.format(edge.length)))
                    total_length += edge.length
                    
        # while edges_left > 0:
        #     edge = node.neighbors[2]
        #     path_edges.append( (edge.src.loc, edge.dest.loc, '{:.0f}'.format(edge.length)) )
        #     total_length += edge.length
        #     node = edge.dest
        #     edges_left -= 1
        return {'cost':total_length, 'path':path_edges}

    def computeShortestPaths( self, srcIndex, use_heap=False ):
        self.source = srcIndex
        t1 = time.time()
        if use_heap:
            self.queue = HeapQueue()
        else:
            self.queue = ArrayQueue()

        self.dist = dict()
        self.prev = dict()
        nodes = self.network.getNodes()
        for node in nodes:
            self.queue.insert(node, float('inf'))
            self.dist[node.node_id] = float('inf')
            self.prev[node.node_id] = None
        self.queue.decrease_key(srcIndex, 0)
        self.dist[srcIndex] = 0 
        while self.queue.queue:
            try:
                pop_dist, _, pop_node = self.queue.delete_min()
                for edge in pop_node.neighbors:
                    if self.dist[edge.dest.node_id] > self.dist[pop_node.node_id] + edge.length:
                        self.dist[edge.dest.node_id] = self.dist[pop_node.node_id] + edge.length
                        self.prev[edge.dest.node_id] = pop_node
                        self.queue.decrease_key(edge.dest.node_id, self.dist[edge.dest.node_id])
            except:
                pass


        t2 = time.time()
        return (t2-t1)


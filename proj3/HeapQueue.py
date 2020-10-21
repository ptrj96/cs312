import heapq
from heapq import heappop, heappush
class HeapQueue(object):
    def __init__(self):
        self.queue = []
        self.queue_map = dict()

    def insert(self, node, dist):
        # time complexity of O(log(n)) for inserting to binary heap
        ins = [dist, node]
        self.queue_map[node.node_id] = ins
        heappush(self.queue, ins)
    
    def delete_min(self):
        # time complexity of O(log(n)) for deleting from binary heap
        while self.queue:
            pop = heappop(self.queue)
            if pop[-1] != 'edited':
                del self.queue_map[pop[-1].node_id]
                return pop

    def decrease_key(self, key, dist):
        # time complexity of O(log(n)) to insert new edited node to 
        # binary heap
        if key in self.queue_map:
            ins = [dist, self.queue_map[key][-1]]
            self.queue_map[key][-1] = 'edited'
            self.queue_map[key] = ins
            heappush(self.queue, ins)
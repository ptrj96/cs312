class ArrayQueue(object):
    def __init__(self):
        self.queue = []
        self.queue_map = dict()
    
    def insert(self, node, dist):
        # time complexity of O(1) to insert to array and map
        self.queue.append(node)
        self.queue_map[node.node_id] = (dist)

    def delete_min(self):
        # time complexity of O(n) as it has to iterate over all
        # of the indexes of the array
        min_index = 0
        for i in range(len(self.queue)):
            if self.queue_map[self.queue[i].node_id] < self.queue_map[self.queue[min_index].node_id]:
                min_index = i
        item = self.queue[min_index]
        dist = self.queue_map[item.node_id]
        del self.queue[min_index]
        return dist, item
    
    def decrease_key(self, key, dist):
        # time complexity of O(1) to edit value in map
        self.queue_map[key] = dist

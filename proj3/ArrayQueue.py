class ArrayQueue(object):
    def __init__(self):
        self.queue = []
    
    def insert(self, node, dist):
        self.queue.append([dist, node])

    def delete_min(self):
        min_index = 0
        for i in range(len(self.queue)):
            if self.queue[i][0] < self.queue[min_index][0]:
                min_index = i
        item = self.queue[min_index]
        del self.queue[min_index]
        return item
    
    def decrease_key(self, key, dist):
        for item in self.queue:
            if item[-1].node_id == key:
                item[0] = dist

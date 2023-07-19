from multiprocessing.managers import BaseManager
import multiprocessing as mp
from . import util_ixpe

# abstract class
class CacheAPI:
    def get_edge_position(self):
        return

    def set_edge_position(self, pos):
        return

    def cacher_hit(self, side, frame):
        return

    def cacher_update(self, side, frame = None, result = None):
        return

class CacheAPI_impl(CacheAPI):
    def __init__(self):
        super().__init__()
        self.b_mgr = BaseManager()
        self.b_mgr.register('CachePool', util_ixpe.CachePool)
        self.b_mgr.start()
        self.cacher = self.b_mgr.CachePool()

        self.mgr = mp.Manager()
        self.edge_position = self.mgr.list([0,0])
    # should be using an outside db service to store the status
    def get_edge_position(self):
        return self.edge_position[0], self.edge_position[1]

    # should be using an outside db service to store the status
    def set_edge_position(self, pos):
        self.edge_position[0] = pos[0]
        self.edge_position[1] = pos[1]
        # pos should be a list of two numbers: [a, b]
        return

    # should be using an outside cache service to store the status
    def cacher_hit(self, side, frame):
        return self.cacher.hit(side, frame)

    # should be using an outside cache service to store the status
    def cacher_update(self, side, frame = None, result = None):
        return self.cacher.update(side, frame, result)

if __name__ == '__main__':
    pass
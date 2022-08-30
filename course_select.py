import time
import _thread
from utils.course_selector import Selector

gap, threads = 1, 2
cid, c_type = 'B3I392100', '核心专业'
selectors = [Selector(cid, c_type) for _ in range(threads)]


def invoke(index):
    selectors[index].select()


if __name__ == '__main__':
    while True:
        for i in range(threads):
            _thread.start_new_thread(invoke, (i,))
        time.sleep(gap)

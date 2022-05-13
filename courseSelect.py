import time
import _thread
from utils.courseSelector import Selector

GAP, THREADS = 1, 10


def invoke():
    Selector('2021-2022', '1', 'B3J114514', '一般专业').select()


if __name__ == '__main__':
    while True:
        for i in range(THREADS):
            _thread.start_new_thread(invoke, ())
        time.sleep(GAP)

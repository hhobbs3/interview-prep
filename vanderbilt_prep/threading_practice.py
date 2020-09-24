import threading
from queue import Queue
import time

print_lock = threading.Lock()
q = Queue()

def example_job(worker):
    time.sleep(0.5)
    with print_lock:
        print(threading.current_thread().name, worker)

def threader():
    while True:
        worker = q.get()
        example_job(worker)
        q.task_done()

def threading_example():
    for x in range(10):  # create 10 available threads
        t = threading.Thread(target=threader)
        t.daemon = True  # kill threads when you don't need them anymore
        t.start()

    start = time.time()

    for worker in range(20):  # 20 jobs to be run
        q.put(worker)

    q.join()

    print("Entire job took: ", time.time() - start)

def threading_control_example():
    start = time.time()
    for worker in range(20):  # 20 jobs to be run
        time.sleep(0.5)
        print(f"Completed: {worker}")
    print("Entire job took: ", time.time() - start)

if __name__ == '__main__':
    threading_example()
    threading_control_example()
import multiprocessing as mp
import time

# Tutorial
# https://www.youtube.com/watch?v=CRJOQtaRT_8
# https://www.youtube.com/watch?v=HxGC8y0o_Cg

"""
Core Concepts
    1. Process: creates a process identifier to run as independent OS child processes; start: begins execution of 
        process, join: terminates the execution of the process.
    2. Lock: helps to lock the code during execution by a Process; acquire: creates the lock, release: removes lock.
    3. Queue: provides shared data for multiple processes; insert: put, consume: get
    4. Pool: provides data parallelism
        
"""


def print_value(val):
    print(val)

def square_root(val, q):
    q.put(val * val)

def multiprocessing_lang():
    languages = ['C', 'Python', 'JAVA', 'PHP']
    processes = []

    start = time.time()
    for language in languages:
        proc = mp.Process(target=print_value, args=(language,))  # initiate process
        processes.append(proc)
        proc.start()  # Starts them as they are looped through.

    for p in processes:  # must be joined before they can be used
        p.join()
    print("Entire job took: ", time.time() - start)

    start = time.time()
    for language in languages:
        print_value(language)
    print("Entire job took: ", time.time() - start)


def multiprocessing_sqr():
    q = mp.Queue()

    # initiate processes
    processes = [mp.Process(target=square_root, args=(i, q))for i in range(2, 10)]  # create a sqr process for 2-9

    # start processes
    for p in processes:
        p.start()

    # join processes
    for p in processes:
        p.join()

    # get and then print result
    result = [q.get() for p in processes]
    print(result)

def tasks_execute(tasks_data):
    print(f'Process {tasks_data[0]} waiting {tasks_data[1]} seconds')
    time.sleep(int(tasks_data[1]))
    print(f"Process {tasks_data[1]} finished")

def pool_testing():
    tasks = (["A", 5], ["B", 2], ["C", 1], ["D", 3])
    p = mp.Pool(2)  # runs 2 at a time
    p.map(tasks_execute, tasks)


if __name__ == '__main__':
    multiprocessing_lang()
    multiprocessing_sqr()
    pool_testing()
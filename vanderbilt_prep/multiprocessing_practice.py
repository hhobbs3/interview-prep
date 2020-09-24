import multiprocessing as mp
import time

# Tutorial
# https://www.youtube.com/watch?v=CRJOQtaRT_8
# https://www.youtube.com/watch?v=HxGC8y0o_Cg

def print_value(val):
    print(val)

def multiprocessing():
    languages = ['C', 'Python', 'JAVA', 'PHP']
    processes = []

    start = time.time()
    for language in languages:
        proc = mp.Process(target=print_value, args=(language,))
        processes.append(proc)
        proc.start()  # Starts them as they are looped through.
    for p in processes:
        p.join()
    print("Entire job took: ", time.time() - start)

    start = time.time()
    for language in languages:
        print_value(language)
    print("Entire job took: ", time.time() - start)


if __name__ == '__main__':
    multiprocessing()
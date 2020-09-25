from numba import jit
import math
import time

@jit  # takes 1.2 seconds with jit, 19 seconds without jit
def is_prime(number):
    for i in range(2, int(number/2), 1):  # start, stop, increment
        if number % i == 0:
            return False
    return True

def first_n_prime_numbers(n):
    n_prime_numbers = [2, 3]

    count = 2
    six_counter = 6
    while count < n:
        six_minus_one = six_counter - 1
        if (is_prime(six_minus_one)):
            n_prime_numbers.append(six_minus_one)
            count += 1
            if not count < n:
                break
        six_plus_one = six_counter + 1
        if (is_prime(six_plus_one)):
            n_prime_numbers.append(six_plus_one)
            count += 1
        six_counter += 6
    print(n_prime_numbers)
    return n_prime_numbers


if __name__ == '__main__':
    start = time.time()
    n = 10000
    n_prime_numbers = first_n_prime_numbers(n)
    print(len(n_prime_numbers))
    assert len(n_prime_numbers) == n
    print("run time: ", time.time() - start)
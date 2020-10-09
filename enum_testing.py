
def enum_test(nums, k):
    lastSeen = {}
    for i, n in enumerate(nums):
        if n in lastSeen:
            if i - lastSeen[n] <= k:
                return True
            else:
                lastSeen[n] = i
        else:
            lastSeen[n] = i
    return False

if __name__ == "__main__":
    enum_test([0, 1, 2, 3, 5, 2], 3)
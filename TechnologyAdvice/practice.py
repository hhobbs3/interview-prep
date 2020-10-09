class Song:
    def __init__(self, name):
        self.name = name
        self.next = None

    def next_song(self, song):
        self.next = song

    def is_repeating_playlist(self):
        """
        :returns: (bool) True if the playlist is repeating, False if not.
        """
        song = self
        song_list = set()
        while song:
            song_list.add(song)
            song = song.next
            if song in song_list:
                return True
        return False


first = Song("Hello")
second = Song("Eye of the tiger")

first.next_song(second)
second.next_song(first)

print(first.is_repeating_playlist())


# import collections
#
# Node = collections.namedtuple('Node', ['left', 'right', 'value'])
#
# def contains(root, value):
#     if root is None:
#         return False
#     if root.value == value:
#         return True
#     if root.value < value:
#         return contains(root.right, value)
#     return contains(root.left, value)
#
#
# n1 = Node(value=1, left=None, right=None)
# n3 = Node(value=3, left=None, right=None)
# n2 = Node(value=2, left=n1, right=n3)
#
# print(contains(n2, 3))
#
#
# def group_by_owners(files):
#     return None
#
# if __name__ == "__main__":
#     files = {
#         'Input.txt': 'Randy',
#         'Code.py': 'Stan',
#         'Output.txt': 'Randy'
#     }
#     print(group_by_owners(files))


#from itertools import permutations
#
#class IceCreamMachine:
#
#    def __init__(self, ingredients, toppings):
#        self.ingredients = ingredients
#        self.toppings = toppings
#
#    def scoops(self):
#        options = []
#        for i in range(len(self.ingredients)):
#            for j in range(len(self.toppings)):
#                options.append([self.ingredients[i], self.toppings[j]])
#        return options
#
#if __name__ == "__main__":
#    machine = IceCreamMachine(["vanilla", "chocolate"], ["chocolate sauce"])
#    print(machine.scoops())  # should print[['vanilla', 'chocolate sauce'], ['chocolate', 'chocolate sauce']]



# def group_by_owners(files):
#     owner = {}
#     for k, v in files.items():
#         print(f"k: {k}, v: {v}")
#         if v in owner:
#             owner[v].append(k)
#         else:
#             owner[v] = [k]
#     return owner
#
# if __name__ == "__main__":
#     files = {
#         'Input.txt': 'Randy',
#         'Code.py': 'Stan',
#         'Output.txt': 'Randy'
#     }
#     print(group_by_owners(files))




# def unique_names(names1, names2):
#     x = set()
#     for name in names1:
#         x.add(name)
#     for name in names2:
#         x.add(name)
#     return list(x)
#
# if __name__ == "__main__":
#     names1 = ["Ava", "Emma", "Olivia"]
#     names2 = ["Olivia", "Sophia", "Emma"]
#     print(unique_names(names1, names2)) # should print Ava, Emma, Olivia, Sophia
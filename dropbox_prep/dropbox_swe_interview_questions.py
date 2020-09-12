"""
Dropbox specific practice based on https://www.pathrise.com/companies/dropbox
"""
import collections
import re
import random
import string
from pymongo_helper_functions import PymongoHelperFunctions
import datetime


class DropBoxChallenges:

    def __init__(self):
        self.code_to_long_url = {}
        self.alphanumerics = string.ascii_letters + '0123456789'

    def lists_and_sums_of_elements(self):
        pass


    def locate_specific_word_in_dictionary(self):
        pass


    def pattern_and_string_match(self, pattern: str, string: str):
        """
        Compare a pattern to a string
        :param pattern: str
        :param string: str
        :return: boolean
        """
        map_char = {}
        map_word = {}

        words = string.split()
        if(len(words) != len(pattern)):  # if lengths don't match, they can't match
            return False
        for pattern_char, word in zip(pattern, words):
            if pattern_char not in map_char:  # if True, then pattern_char hasn't been encountered yet
                if word in map_word:  # if True, then the word has been encountered before
                    return False  # there is a mismatch between pattern_char and word
                else:  # it is a new pattern_char word match
                    map_char[pattern_char] = word
                    map_word[word] = pattern_char
            else:  # we have encountered a familiar pattern_char
                if map_char[pattern_char] != word:  # if True, then the associated word does not match
                    return False

        return True

    def find_duplicate_files(self, paths):
        """
        Find files that are duplicates
        :param paths:  List[str]
        :return: List[List[str]]
        """

        path_dic = {}
        for path in paths:
            path_values = path.split()
            root = path_values[0]
            # file_path = path_values[0] = path
            iter_values_in_path = iter(path_values)
            next(iter_values_in_path)
            for value in iter_values_in_path:
                if "(" in value:
                    content_start = value.find("(")
                    file_content = value[content_start:].replace("(", "").replace(")", "")
                    file_name = value[:content_start]
                    print(f"testing: {[(root + '/' + file_name)]}")
                    if file_content in path_dic.keys():
                        path_dic[file_content] += [(root + "/" + file_name)]
                    else:
                        path_dic[file_content] = [(root + "/" + file_name)]
        duplicates_list = []
        for key in path_dic:
            if len(path_dic[key]) > 1:
                duplicates_list.append(path_dic[key])
        return duplicates_list

    def find_duplicate_files_regex(self, paths):
        ans = collections.defaultdict(list)
        for files in paths:
            f = iter(files.split())
            prefix = next(f)
            for file in f:
                name, content = re.match(r'(\S+)\((\S+)\)', file).groups() # ('1.txt', 'abcd')
                ans[content].append('{}/{}'.format(prefix, name))
        return [v for v in ans.values() if len(v)>1]

    def find_duplicate_files_fast(self, paths):
        locations = collections.defaultdict(list)

        for i in paths:
            comps = i.split(' ')
            root = comps[0]
            files = comps[1:]

            for f in files:
                f = f.rstrip(')')  # remove )
                f, k = f.split('(')  # split it at ( and put file name in f and content into k
                locations[k].append(root + '/' + f)

        return [x for x in locations.values() if len(x) > 1]


    def encode_url(self, longUrl: str):
        """Encodes a URL to a shortened URL.
        """
        code = ''.join(random.choice(self.alphanumerics) for _ in range(6))

        while code in self.code_to_long_url:
            code = ''.join(random.choice(self.alphanumerics) for _ in range(6))

        self.code_to_long_url[code] = longUrl

        return f'http://tinyurl.com/{code}'

    def decode_url(self, shortUrl):
        """Decodes a shortened URL to its original URL.
                """
        return self.code_to_long_url[shortUrl.split('/')[-1]]


    def log_hits(self, time_in_min):
        pymongo = PymongoHelperFunctions
        current_time = datetime.datetime.now()
        fifteen_minutes_ago = current_time - datetime.timedelta(minutes=time_in_min)
        hit = {"hit_time": current_time}
        collection_name = "hits"
        pymongo.insert(pymongo, document=hit, collection_name=collection_name)
        num_hits = len(pymongo.find(pymongo, query={"hit_time": {"$gt": fifteen_minutes_ago}}, collection_name=collection_name))
        return num_hits

if __name__ == "__main__":
    dropbox_challenges = DropBoxChallenges()

    print(f"pattern_and_string_match: {dropbox_challenges.pattern_and_string_match('abba', 'cat dog dog cat')}")

    files = ["root/a 1.txt(abcd) 2.txt(efgh)", "root/c 3.txt(abcd)", "root/c/d 4.txt(efgh)", "root 4.txt(efgh)"]
    print(f"find_duplicate_files: {dropbox_challenges.find_duplicate_files(files)}")
    print(f"find_duplicate_files_regex: {dropbox_challenges.find_duplicate_files_regex(files)}")
    print(f"find_duplicate_files_fast: {dropbox_challenges.find_duplicate_files_fast(files)}")

    encode = dropbox_challenges.encode_url('https://leetcode.com/problems/design-tinyurl')
    print(f"encode: {encode}")
    print(f"decode: {dropbox_challenges.decode_url(encode)}")

    print(f"log_hits: {dropbox_challenges.log_hits(15)}")


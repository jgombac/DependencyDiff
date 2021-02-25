from typing import List
from commandline import run_semantic
from test_data import *
import json

'''
This
Identifier
Call
MemberAccess
Empty
'''


def item_generator(json_input, lookup_key):
    if isinstance(json_input, dict):
        for k, v in json_input.items():
            if k == lookup_key:
                yield json_input
            else:
                yield from item_generator(v, lookup_key)
    elif isinstance(json_input, list):
        for item in json_input:
            yield from item_generator(item, lookup_key)


class Semantic:
    trees = test_trees

    def __init__(self, workdir: str, filenames: List[str]):
        self.workdir = workdir
        self.filenames = filenames

    def __parse(self):
        return run_semantic(self.workdir, self.filenames)

    def get_trees(self):
        if self.trees:
            return self.trees
        parse_results = self.__parse()
        self.trees = list(
            filter(lambda tree_list: tree_list.get("tree"), parse_results["trees"]))
        return self.trees

    def get_file_tree(self, filename: str):
        tree = next((tree for tree in self.get_trees()
                     if tree["path"] == "/workspace/" + filename), None)
        if tree:
            return tree["tree"]
        raise Exception("No file '{}' in trees".format(filename))

    def get_items_in_line(self, file_tree, line_num: int):
        return list(filter(lambda item: item["sourceSpan"]["start"][0] == line_num, item_generator(file_tree, "term")))

    def get_identifiers(self, file_tree):
        return list(filter(lambda item: item["term"] == "Identifier", item_generator(file_tree, "term")))

    def get_identifiers_in_line(self, file_tree, line_num: int):
        return list(filter(lambda item: item["term"] == "Identifier" and item["sourceSpan"]["start"][0] == line_num, item_generator(file_tree, "term")))

    def get_calls_in_line(self, file_tree, line_num: int):
        return list(filter(lambda item: item["term"] == "Call" and item["sourceSpan"]["start"][0] == line_num, item_generator(file_tree, "term")))

    def construct_calls(self, call):
        def get_token(hand_side):
            calls = []

            if not hand_side:
                return calls

            _call = {}
            if hand_side["term"] == "This":
                _call["name"] = "this"
            elif hand_side["term"] == "Identifier" and hand_side.get("name"):
                _call["name"] = hand_side.get("name")
            elif hand_side["term"] == "Call":
                _call["parameters"] = list(map(
                    lambda param: param.get("name"), hand_side["callParams"]))
            if _call:
                calls.append(_call)
            if hand_side["term"] in ["Call", "MemberAccess"]:
                calls.extend(internal(hand_side, []))
            return calls

        def internal(call, storage):
            calls = []

            if call["term"] == "Call":
                calls.extend(internal(call["callFunction"], []))
            elif call["term"] == "MemberAccess":
                calls.extend(get_token(call.get("lhs")))
                calls.extend(get_token(call.get("rhs")))

            storage.extend(calls)
            return storage

        return internal(call, [])


def scrub(obj, bad_key="_this_is_bad"):
    if isinstance(obj, dict):
        # the call to `list` is useless for py2 but makes
        # the code py2/py3 compatible
        for key in list(obj.keys()):
            if key == bad_key:
                del obj[key]
            else:
                scrub(obj[key], bad_key)
    elif isinstance(obj, list):
        for i in reversed(range(len(obj))):
            if obj[i] == bad_key:
                del obj[i]
            else:
                scrub(obj[i], bad_key)

    else:
        # neither a dict nor a list, do nothing
        pass


if __name__ == '__main__':
    semantic = Semantic(test_workdir, test_files)
    tree = semantic.get_file_tree(test_files[0])
    line_items = semantic.get_items_in_line(tree, 25)
    terms = semantic.get_identifiers_in_line(tree, 21)
    calls = semantic.get_calls_in_line(tree, 25)
    for item in line_items:
        scrub(item, "sourceRange")
        scrub(item, "sourceSpan")
        scrub(item, "callContext")
        scrub(item, "callBlock")
        print(item, "\n")
    print("CALLS")
    for call in calls:
        print(semantic.construct_calls(call), "\n")
    #print(line_items, terms)

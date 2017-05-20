# USC CSCI 561 Spring 2017 Project 3
# Bayes Network Inference
# Copyright 2017 Cccmm002


import sys
import copy
import collections
from abc import ABCMeta, abstractmethod


class BayesRecord(collections.Mapping):    # FrozenDict: {(Name: Boolean)}
    def __init__(self, d):
        self._d = d
        self._hash = None

    def __str__(self):
        res = []
        for k in self._d:
            res.append(k + ": " + str(self._d[k]))
        return "{" + ", ".join(res) + "}"

    def __iter__(self):
        return iter(self._d)

    def __len__(self):
        return len(self._d)

    def __getitem__(self, item):
        return self._d[item]

    def __eq__(self, other):
        return self._d == other._d

    def __ne__(self, other):
        return not (self == other)

    def __deepcopy__(self, memo):
        res = BayesRecord(dict(self._d))
        res._hash = self._hash
        return res

    def __hash__(self):
        if self._hash is None:
            self._hash = 0
            for k in self._d.keys():
                self._hash ^= hash((k, self._d[k]))
        return self._hash

    def dict(self):
        return dict(self._d)


class Node(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def probability(self, value, precond):  # value = True or False; precond = {'A': True, 'B': False}
        return NotImplemented

    @abstractmethod
    def parents(self):
        return NotImplemented

    @abstractmethod
    def is_parent(self, node):
        return NotImplemented


class Chance(Node):
    def __init__(self, record_dict):
        self._d = copy.deepcopy(record_dict)   # Dict: {(BayesRecord, Float)}
        self._parents = None

    def __str__(self):
        res = []
        for k in self._d:
            res.append(str(k) + ": " + str(self._d[k]))
        return "{" + ", ".join(res) + "}"

    def probability(self, value, precond):
        keys = self._d.keys()[0].keys()
        d = dict()
        for k in keys:
            d[k] = precond[k]
        br = BayesRecord(d)
        return self._d[br] if value else 1 - self._d[br]

    def parents(self):
        if self._parents is None:
            self._parents = self._d.keys()[0].keys()
        return self._parents

    def is_parent(self, node):
        return node in self.parents()


class ChanceRoot(Node):
    def __init__(self, p):
        self.prob = p

    def __str__(self):
        return str(self.prob)

    def probability(self, value, precond):
        return self.prob if value else 1 - self.prob

    def parents(self):
        return []

    def is_parent(self, node):
        return False


class Utility(Node):
    def __init__(self, record_dict):
        self._d = record_dict   # Dict: {(BayesRecord, Int)}
        self._parents = None

    def __str__(self):
        res = []
        for k in self._d:
            res.append(k + ": " + str(self._d[k]))
        return "{" + ", ".join(res) + "}"

    def __getitem__(self, key):
        return self._d[key]

    def keys(self):
        return self._d.keys()

    def probability(self, value, precond):
        return NotImplemented

    def parents(self):
        if self._parents is None:
            self._parents = self._d.keys()[0].keys()

    def is_parent(self, node):
        return node in self.parents()


class Decision(Node):
    def __init__(self):
        pass

    def probability(self, value, precond):
        return 1

    def parents(self):
        return []

    def is_parent(self, node):
        return False


def enum_helper(kl):
    if len(kl) == 1:
        return [{kl[0]: True}, {kl[0]: False}]
    else:
        nextlist = enum_helper(kl[1:])
        truelist = copy.deepcopy(nextlist)
        for d in truelist:
            d[kl[0]] = True
        falselist = copy.deepcopy(nextlist)
        for d in falselist:
            d[kl[0]] = False
        return truelist + falselist


class BayesNetwork:
    def __init__(self):
        self.node_dict = dict()
        self._sorted_nodes = None
        self._computed = dict()

    def __str__(self):
        res = []
        for k in self.node_dict:
            res.append(k + ": " + str(self.node_dict[k]))
        return "{" + ", ".join(res) + "}"

    def topological_sort(self):
        all_nodes = self.node_dict.keys()
        # Reversed topological sort to get list of all nodes
        counts = dict()
        for n in all_nodes:
            if n == 'utility':
                continue
            counts[n] = 0
        for n in all_nodes:
            if n == 'utility':
                continue
            l = self.node_dict[n].parents()
            for item in l:
                counts[item] += 1
        s = collections.deque()
        for key in counts:
            if counts[key] == 0:
                s.append(key)
        rev_topo = []
        while len(s) > 0:
            n = s.popleft()
            rev_topo.append(n)
            pl = self.node_dict[n].parents()
            for item in pl:
                counts[item] -= 1
                if counts[item] == 0:
                    s.append(item)
        self._sorted_nodes = rev_topo[::-1]

    def variables(self):
        if self._sorted_nodes is None:
            self.topological_sort()
        return self._sorted_nodes

    def expected_utility(self, query, precond):
        unode = self.node_dict['utility']
        pc = precond if precond is not None else dict()
        for k in query:
            pc[k] = query[k]
        res = 0
        for by in unode.keys():
            dby = by.dict()
            p = self.query_probability(dby, pc)
            res += p * unode[by]
        return res

    def maximum_expected_utility(self, query, precond):
        dl = enum_helper(query.keys())
        max_utility = 0 - sys.maxint
        max_situation = None
        for item in dl:
            cur = self.expected_utility(item, precond)
            if cur > max_utility:
                max_utility = cur
                max_situation = item
        reverse = dict()
        for k in query:
            reverse[query[k]] = max_situation[k]
        text = ""
        for i in range(len(reverse)):
            if i in reverse:
                text += '+ ' if reverse[i] else '- '
        text += str(int(round(max_utility)))
        return text

    def query_probability(self, query, precond):   # query: {'A': True}, precond: {'B': True}
        if precond is None:
            precond = dict()

        for kpc in precond:
            if kpc in query:
                if query[kpc] == precond[kpc]:
                    del query[kpc]
                else:
                    return 0

        distribution = dict()
        ql = query.keys()
        if len(ql) == 0:
            return 1.0
        dl = enum_helper(ql)
        for item in dl:
            br = BayesRecord(item)
            distribution[br] = None

        for k in distribution:
            if distribution[k] is not None:
                continue
            e = copy.deepcopy(precond)
            for key in k:
                e[key] = k[key]
            distribution[k] = self.enumerate_all(0, e)

        total = 0
        for k in distribution:
            total += distribution[k]
        if total > 0:
            for k in distribution:
                distribution[k] = distribution[k] / total
        qbr = BayesRecord(query)
        return distribution[qbr]

    def enumerate_all(self, vars_index, e):   # vars_index: index in self.variables(), e: {'D': True, 'E': False}
        if vars_index == len(self._sorted_nodes) or len(e) == 0:
            return 1.0
        computed_dict_key = (BayesRecord(e), vars_index)
        if computed_dict_key in self._computed:
            return self._computed[computed_dict_key]

        flag = True
        for nn in e.keys():
            if nn not in self._sorted_nodes[:vars_index]:
                flag = False
                break
        if flag:
            self._computed[computed_dict_key] = 1
            return 1

        y = self._sorted_nodes[vars_index]
        ne = dict(e)

        for nn in self._sorted_nodes[:vars_index + 1]:
            not_a_parent = True
            for after in self._sorted_nodes[vars_index + 1:]:
                if self.node_dict[after].is_parent(nn):
                    not_a_parent = False
                    break
            if not_a_parent:
                if nn in ne:
                    del ne[nn]

        if y in e:
            res = self.node_dict[y].probability(e[y], e) * self.enumerate_all(vars_index + 1, ne)
        else:
            ne[y] = True
            num_true = self.node_dict[y].probability(True, e) * self.enumerate_all(vars_index + 1, ne)
            ne[y] = False
            num_false = self.node_dict[y].probability(False, e) * self.enumerate_all(vars_index + 1, ne)
            res = num_true + num_false
        self._computed[computed_dict_key] = res
        return res


def bn_parser(string_list, bn):
    if string_list[1] == "decision":
        cur = Decision()
        bn.node_dict[string_list[0]] = cur
    else:
        first_line = map(lambda x: x.strip(), string_list[0].split('|'))
        record_dict = dict()
        if len(first_line) <= 1:
            cur = ChanceRoot(float(string_list[1]))
            bn.node_dict[first_line[0]] = cur
            return
        parent_list = first_line[1].split(' ')
        for i in range(1, len(string_list)):
            line = string_list[i].split(' ')
            bayes = dict()
            for j in range(1, len(line)):
                bayes[parent_list[j - 1]] = line[j] == '+'
            br = BayesRecord(bayes)
            record_dict[br] = float(line[0])
        if first_line[0] == "utility":
            cur = Utility(record_dict)
        else:
            cur = Chance(record_dict)
        bn.node_dict[first_line[0]] = cur


def query_parser(queries, bn):
    res_text = []
    for q in queries:
        lb = q.index('(')
        rb = q.index(')')
        func = q[:lb]
        inside = map(lambda x: x.strip(), q[lb + 1:rb].split('|'))
        query = dict()
        isc = inside[0].split(', ')
        for i in range(len(isc)):
            equal = map(lambda x: x.strip(), isc[i].split('='))
            if len(equal) > 1:
                query[equal[0]] = equal[1] == '+'
            else:   # MEU queries
                query[equal[0]] = i   # i means order
        precond = None
        if len(inside) > 1:
            precond = dict()
            for qi in inside[1].split(', '):
                equal = qi.split(' = ')
                precond[equal[0]] = equal[1] == '+'
        if func == 'P':
            res_text.append("{:.2f}".format(bn.query_probability(query, precond)))
        elif func == 'EU':
            res_text.append(str(int(round(bn.expected_utility(query, precond)))))
        elif func == 'MEU':
            res_text.append(bn.maximum_expected_utility(query, precond))
    return res_text


def main():
    infile = open("input.txt", "r")
    queries = []
    while True:
        query_string = infile.readline().strip('\n').strip('\r')
        if query_string == "******":
            break
        queries.append(query_string)
    bn = BayesNetwork()
    cur_parser_list = []
    while True:
        line = infile.readline().strip('\n').strip('\r')
        if line == "" or line == " ":
            bn_parser(cur_parser_list, bn)
            break
        if line == "***" or line == "******":
            bn_parser(cur_parser_list, bn)
            cur_parser_list = []
        else:
            cur_parser_list.append(line)

    bn.topological_sort()
    res = query_parser(queries, bn)
    output_file = open('output.txt', 'w+')
    output_file.write('\n'.join(res))
    output_file.close()


if __name__ == '__main__':
    main()

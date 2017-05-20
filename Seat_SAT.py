# USC CSCI 561 Spring 2017 Project 2
# Propositional Logic
# Copyright 2017 Cccmm002


import itertools
import random
import copy


class Literal:
    def __init__(self, g, t):
        self.guest = g
        self.table = t

    def __str__(self):
        return '(' + str(self.guest) + ', ' + str(self.table) + ')'

    def __eq__(self, other):
        return self.guest == other.guest and self.table == other.table

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return 31*self.guest + self.table    # return hash((self.guest, self.table))

    def __copy__(self):
        return Literal(self.guest, self.table)


class Clause:
    def __init__(self):
        self.literals = dict()

    def add(self, literal, negate):
        self.literals[literal] = negate

    def is_empty(self):
        return len(self.literals) == 0

    def has_unique(self):
        return len(self.literals) == 1

    def satisfy(self, model):
        for k in self.literals:
            if self.literals[k] == model[k]:
                return True
        return False

    def __eq__(self, other):
        return self.literals == other.literals

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(frozenset(self.literals.items()))

    def __str__(self):
        res = "(size: " + str(len(self.literals)) + '): '
        rl = []
        for k in self.literals:
            rl.append(str(k) + str(self.literals[k])[0])
        return res + ', '.join(rl)

    def __copy__(self):
        res = Clause()
        for k in self.literals:
            res.add(k, self.literals[k])
        return res


class Model:
    def __init__(self, symbols):
        self.content = dict()
        for s in symbols:
            ns = copy.copy(s)
            self.content[ns] = True if random.random() > 0.5 else False

    def __getitem__(self, para):
        return self.content[para]

    def __setitem__(self, para, value):
        self.content[para] = value


class UnionFind:
    def __init__(self):
        self.weights = {}
        self.parents = {}

    def __getitem__(self, object):
        if object not in self.parents:
            self.parents[object] = object
            self.weights[object] = 1
            return object
        path = [object]
        root = self.parents[object]
        while root != path[-1]:
            path.append(root)
            root = self.parents[root]
        for ancestor in path:
            self.parents[ancestor] = root
        return root

    def __iter__(self):
        return iter(self.parents)

    def union(self, *objects):
        roots = [self[x] for x in objects]
        heaviest = max([(self.weights[r], r) for r in roots])[1]
        for r in roots:
            if r != heaviest:
                self.weights[heaviest] += self.weights[r]
                self.parents[r] = heaviest


def deepcopy_cnf(cnf):
    res = set()
    for c in cnf:
        res.add(copy.copy(c))
    return res


def dpll(kb, symset):
    clauses = kb
    symbols = symset
    while True:
        # Pure symbol
        symbols_to_be_deleted = set()
        for s in symbols:
            v = None
            pure = True
            for c in clauses:
                if s not in c.literals:
                    continue
                if v is None:
                    v = c.literals[s]
                else:
                    if not v == c.literals[s]:
                        pure = False
                        break
            if pure:
                symbols_to_be_deleted.add(s)
        clauses_to_be_deleted = set()
        for s in symbols_to_be_deleted:
            for c in clauses:
                if s in c.literals:
                    clauses_to_be_deleted.add(c)
        for c in clauses_to_be_deleted:
            clauses.remove(c)
        for s in symbols_to_be_deleted:
            symbols.remove(s)
        # Unit clause rule
        clauses_to_be_deleted = set()
        for cur in clauses:
            if not cur.has_unique():
                continue
            sym_bool = cur.literals.items()[0]
            clauses_to_be_deleted.add(cur)
            for c in clauses:
                if c == cur:
                    continue
                if sym_bool[0] in c.literals:
                    if sym_bool[1] == c.literals[sym_bool[0]]:   # Delete the whole clause
                        clauses_to_be_deleted.add(c)
                    else:    # Delete the literal
                        c.literals.pop(sym_bool[0])
                        if c.is_empty():
                            return False
        clauses = set(list(clauses))
        for c in clauses_to_be_deleted:
            if c in clauses:
                clauses.remove(c)
        # DPLL
        if len(clauses) == 0:
            return True
        clauses_a = deepcopy_cnf(clauses)
        clauses_b = deepcopy_cnf(clauses)
        lit = random.sample(symbols, 1)[0]
        clause_t = Clause()
        clause_t.add(copy.copy(lit), True)
        clause_f = Clause()
        clause_f.add(copy.copy(lit), False)
        clauses_a.add(clause_t)
        clauses_b.add(clause_f)
        ra = dpll(clauses_a, symbols.copy())
        if ra:
            return True
        else:
            return dpll(clauses_b, symbols.copy())


def cnf_satisfy(cnf, model):
    for clause in cnf:
        if not clause.satisfy(model):
            return False
    return True


def walkSAT(cnf, p, symbols):  # CNF should be in list instead of set
    model = Model(symbols)
    cnf_length = len(cnf)
    while True:
        if cnf_satisfy(cnf, model):
            return model
        chosen = cnf[0]
        while chosen.satisfy(model):
            chosen = cnf[random.randint(0, cnf_length - 1)]
        syms = list(chosen.literals)
        if random.random() < p:
            r = random.randint(0, len(syms) - 1)
            model[syms[r]] = not model[syms[r]]
        else:
            max_lit = -1
            max_count = -1
            for i in range(0, len(syms)):
                model[syms[i]] = not model[syms[i]]
                count = len([clause for clause in cnf if clause.satisfy(model)])
                model[syms[i]] = not model[syms[i]]
                if count > max_count:
                    max_count = count
                    max_lit = i
            model[syms[max_lit]] = not model[syms[max_lit]]


def output_no():
    file_output = open('output.txt', 'w+')
    file_output.write('no\n')
    file_output.close()


def main():
    f = open("input.txt", "r")
    (m, n) = tuple(map(lambda x: int(x), f.readline().strip('\n').strip('\r').split(' ')))
    rules = {}
    while True:
        line = f.readline()
        split_line = line.strip('\n').strip('\r').split(' ')
        if "" in split_line or " " in split_line:
            break
        pair = frozenset((int(split_line[0]), int(split_line[1])))
        v = split_line[2] == 'F'
        if len(pair) == 1 and v:
            continue
        if (len(pair) == 1 and not v) or (pair in rules and v != rules[pair]):
            output_no()
            f.close()
            return
        rules[pair] = v
    f.close()

    groups = UnionFind()
    enemy_list = []
    for g in range(1, m + 1):
        groups[g]
    for k in rules:
        if rules[k]:
            p = list(k)
            groups.union(p[0], p[1])
    gdict = dict()
    for g in range(1, m + 1):
        k = groups[g]
        if k in gdict:
            gdict[k].add(g)
        else:
            gdict[k] = {g}
    for k in rules:
        if not rules[k]:
            p = list(k)
            if groups[p[0]] == groups[p[1]]:
                output_no()
                return
            else:
                enemy_list.append((groups[p[0]], groups[p[1]]))

    sym_count = len(gdict)
    if sym_count < n:
        n = sym_count
    kb = set()
    symbols = set()
    all_tables = range(1, n + 1)
    for g in gdict.keys():
        onetable = Clause()
        for t in all_tables:
            nl = Literal(g, t)
            symbols.add(nl)
            onetable.add(nl, True)
        kb.add(onetable)
        combination = list(itertools.combinations(all_tables, 2))
        for (a, b) in combination:
            c = Clause()
            c.add(Literal(g, a), False)
            c.add(Literal(g, b), False)
            kb.add(c)
    for k in enemy_list:
        (a, b) = tuple(k)
        for t in all_tables:
            c = Clause()
            c.add(Literal(a, t), False)
            c.add(Literal(b, t), False)
            kb.add(c)

    file_output = open('output.txt', 'w+')
    if not dpll(copy.copy(kb), copy.copy(symbols)):
        file_output.write('no\n')
    else:
        file_output.write('yes\n')
        model = walkSAT(list(kb), 0.5, symbols)
        for g in range(1, m + 1):
            for t in range(1, n + 1):
                if model[Literal(groups[g], t)]:
                    file_output.write(str(g) + ' ' + str(t) + '\n')
                    break
    file_output.close()


if __name__ == '__main__':
    main()

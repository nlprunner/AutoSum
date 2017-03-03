#! /usr/bin/python
# -*- coding: utf8 -*-
BOOK_ID = 0
CHAPTER_ID = 1
SENTENCE_ID = 2
TOKEN_ID = 3
HEAD_ID = 7
WORD = 8
NWORD = 10
ENTITY = 12
SYNTAX = 13
CHARACTER_ID = 15
class Node:
    """node of syntax tree"""
    def __init__(self, nword, nid, ntype, cid):
        self.nword = nword
        self.nid = nid
        self.ntype = ntype
        self.cid = cid
        self.children = []
        self.father = -1
class SyntaxTree:
    """syntax tree"""
    def __init__(self):
        self.root = Node("ROOT", -1, "NONE", -1)
        self.node_map = {}
        self.node_map[-1] = self.root
    def creat(self, sentence):
        for token in sentence:
            #print token
            self.node_map[int(token[TOKEN_ID])] = Node(token[NWORD], int(token[TOKEN_ID]), token[SYNTAX], int(token[CHARACTER_ID]))
        for token in sentence:
            if int(token[TOKEN_ID]) in self.node_map:
                self.node_map[int(token[TOKEN_ID])].father = int(token[HEAD_ID])
            if int(token[HEAD_ID]) in self.node_map:
                self.node_map[int(token[HEAD_ID])].children.append(int(token[TOKEN_ID]))
    def extract_sentence(self, cid):
        """extract sentence"""
        des = []
        output = True
        nsubj = False
        for i in self.node_map.keys():
            temp = self.node_map[i]
            if cid == temp.cid:
                if temp.ntype == 'nsubj' or temp.ntype == 'dobj':
                    nsubj = True
                if output:
                    des.append('PERSON')
                    output = False
            elif temp.nid >= 0:
                des.append(temp.nword)
                output = True
        if nsubj:
            return des
        else:
            return []
    def extract_action(self, cid):
        """extract actions"""
        des = []
        action = -1
        for i in self.node_map.keys():
            temp = self.node_map[i]
            if temp.cid == cid:
                head = temp.father
                if self.node_map[head].ntype == "null":
                    action = head
        if action > -1:
            des.append(self.node_map[action].nword)
            for child in self.node_map[action].children:
                if self.node_map[child].ntype == "dobj":
                    des.append(self.node_map[child].nword)
        return des
    def extract_full_action(self, cid):
        """extract actions"""
        des = []
        outMap = {}
        action = -1
        for i in self.node_map.keys():
            temp = self.node_map[i]
            if temp.cid == cid and (temp.ntype == "nsubj" or temp.ntype == "dobj"):
                head = temp.father
                if head in self.node_map and self.node_map[head].ntype == "null":
                    action = head
        if action > -1:
            outMap[self.node_map[action].nid] = self.node_map[action].nword
            #des.append(self.node_map[action].nword)
            for child in self.node_map[action].children:
                if self.node_map[child].cid == cid:
                    outMap[self.node_map[child].nid] = "PERSON"
                elif self.node_map[child].ntype == "nsubj":
                    outMap[self.node_map[child].nid] = self.node_map[child].nword
                elif self.node_map[child].ntype == "dobj":
                    #des.append(self.node_map[child].nword)
                    outMap[self.node_map[child].nid] = self.node_map[child].nword
                elif self.node_map[child].ntype == "neg":
                    #des.append(self.node_map[child].nword)
                    outMap[self.node_map[child].nid] = self.node_map[child].nword
                elif self.node_map[child].ntype == "aux":
                    #des.append(self.node_map[child].nword)
                    outMap[self.node_map[child].nid] = self.node_map[child].nword
                elif self.node_map[child].ntype == "advmod":
                    outMap[self.node_map[child].nid] = self.node_map[child].nword
        if len(outMap) > 1:
            result = sorted(outMap.items(), lambda x, y: cmp(x[0], y[0]))
            for item in result:
                des.append(item[1])
        return des
    def extract_label(self, cid):
        """
        extract descriptive labels, for example,
        Cop: Mary is [beautiful].
        Amod:  [little] Mary
        """
        des = []
        for i in self.node_map.keys():
            temp = self.node_map[i]
            if temp.cid == cid and temp.ntype == "nsubj":
                head = temp.father
                is_neg = False
                is_cop = False
                if not head in self.node_map:
                    continue
                outMap = {}
                """check head"""
                if self.node_map[head].ntype == "advcl" or self.node_map[head].ntype == "null" or self.node_map[head].ntype == "pcomp" or self.node_map[head].ntype == "xcomp" or self.node_map[head].ntype == "ccomp":
                    outMap[self.node_map[head].nid] = self.node_map[head].nword
                else:
                    continue
                for child in self.node_map[head].children:
                    if self.node_map[child].ntype == "cop" and self.node_map[head].cid == -1:
                        is_cop = True
                    elif self.node_map[child].ntype == "neg":
                        is_neg = True
                    #elif self.node_map[child].ntype == "det":
                    #    outMap[self.node_map[child].nid] = self.node_map[child].nword
                    elif self.node_map[child].ntype == "amod":
                        outMap[self.node_map[child].nid] = self.node_map[child].nword
                    elif self.node_map[child].ntype == "admod":
                        outMap[self.node_map[child].nid] = self.node_map[child].nword
                """create des"""
                if is_cop and len(outMap):
                    #print outMap
                    des_str = ""
                    result = sorted(outMap.items(), lambda x, y: cmp(x[0], y[0]))
                    if is_neg:
                        des_str = "not "
                    for item in result:
                        des_str += (item[1]) + " "
                    des.append(des_str.rstrip())
        return des

    def extract_des(self, cid):
        """extract descriptive properties"""
        des = []
        for i in self.node_map.keys():
            temp = self.node_map[i]
            if temp.cid == cid:
                for child in temp.children:
                    if self.node_map[child].ntype == "amod":
                        #print self.node_map[child].ntype + "\t" + self.node_map[child].nword
                        des.append(self.node_map[child].nword)
                head = temp.father
                if not head in self.node_map:
                    continue
                for child in self.node_map[head].children:
                    if self.node_map[child].ntype == "cop" and self.node_map[head].cid == -1:
                        #print self.node_map[child].ntype + "\t" + self.node_map[head].nword
                        des.append(self.node_map[head].nword)
                    if self.node_map[child].ntype == "advmod":
                        #print self.node_map[child].ntype + "\t" + self.node_map[child].nword
                        des.append(self.node_map[child].nword)
        return des
    def output(self, ):
        #for i in range(len(self.node_map) - 1):
        out = []
        for i in self.node_map.keys():
            temp = self.node_map[i]
            if temp.father in self.node_map:
                out.append(temp.ntype + "(" + self.node_map[temp.father].nword + "-" + str(self.node_map[temp.father].nid) + ", " + temp.nword + "-" + str(temp.nid) + ")")
        return out



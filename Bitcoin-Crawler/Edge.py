__author__ = 'Mathieu'

class Edge:
    def __init__(self,a,b):
        self.a = a
        self.b = b

    def is_implied(self,node):
        return self.a == node or self.b == node
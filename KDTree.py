# -*- coding: utf-8 -*-
"""
Created on Tue Oct 21 21:57:57 2017

@author: Young
"""

class Node(object):
    """ 
    A Node in a kd-tree
    A tree is represented by its root node, and every node represents
    its subtree
    """

    def __init__(self, data=None, left=None, right=None):
        self.data = data
        self.left = left
        self.right = right
    
    @property
    def children(self):
        """
        Returns an iterator for the non-empty children of the Node
        The children are returned as (Node, pos) tuples where pos is 0 for the
        left subnode and 1 for the right.
        """

        if self.left and self.left.data is not None:
            yield self.left, 0
        if self.right and self.right.data is not None:
            yield self.right, 1
            
    def height(self):
        """
        Returns height of the (sub)tree, without considering
        empty leaf-nodes
        """
        min_height = int(bool(self))
        return max([min_height] + [c.height()+1 for c, p in self.children])
    
    def inorder(self):
        """ iterator for nodes: left, root, right """

        if not self:
            return

        if self.left:
            for x in self.left.inorder():
                yield x

        yield self

        if self.right:
            for x in self.right.inorder():
                yield x   
                
class KDNode(Node):
    """ 
    A Node that contains kd-tree specific data and methods
    """

    def __init__(self, data=None, left=None, right=None, axis=None,
            sel_axis=None, dimensions=None):
        """ Creates a new node for a kd-tree
        If the node will be used within a tree, the axis and the sel_axis
        function should be supplied.
        sel_axis(axis) is used when creating subnodes of the current node. It
        receives the axis of the parent node and returns the axis of the child
        node. """
        super(KDNode, self).__init__(data, left, right)
        self.axis = axis
        self.sel_axis = sel_axis
        self.dimensions = dimensions
          
    def is_balanced(self):
        """ 
        Returns True if the (sub)tree is balanced
        The tree is balanced if the heights of both subtrees differ at most by
        1 
        """

        left_height = self.left.height() if self.left else 0
        right_height = self.right.height() if self.right else 0

        if abs(left_height - right_height) > 1:
            return False

        return all(c.is_balanced for c, _ in self.children)

    def rebalance(self):
        """
        Returns the (possibly new) root of the rebalanced tree
        """

        return create([x.data for x in self.inorder()])


def create(point_list=None, dimensions=None, axis=0, sel_axis=None):
    """ Creates a kd-tree from a list of points
    All points in the list must be of the same dimensionality.
    If no point_list is given, an empty tree is created. The number of
    dimensions has to be given instead.
    If both a point_list and dimensions are given, the numbers must agree.
    Axis is the axis on which the root-node should split.
    sel_axis(axis) is used when creating subnodes of a node. It receives the
    axis of the parent node and returns the axis of the child node. """

    if not point_list and not dimensions:
        raise ValueError('either point_list or dimensions must be provided')

    elif point_list:
        dimensions = check_dimensionality(point_list, dimensions)

    # by default cycle through the axis
    sel_axis = sel_axis or (lambda prev_axis: (prev_axis+1) % dimensions)

    if not point_list:
        return KDNode(sel_axis=sel_axis, axis=axis, dimensions=dimensions)

    # Sort point list and choose median as pivot element
    point_list = list(point_list)
    point_list.sort(key=lambda point: point[axis])
    median = len(point_list) // 2
    
    i = median
    #print i
    while (i > 0 and point_list[i-1][axis] == point_list[median][axis]):
        i -= 1
    median = i
    #print i
    loc   = point_list[median]
    left  = create(point_list[:median], dimensions, sel_axis(axis))
    right = create(point_list[median + 1:], dimensions, sel_axis(axis))
    return KDNode(loc, left, right, axis=axis, sel_axis=sel_axis, dimensions=dimensions)


def check_dimensionality(point_list, dimensions=None):
    dimensions = dimensions or len(point_list[0])
    for p in point_list:
        if len(p) != dimensions:
            raise ValueError('All Points in the point_list must have the same dimensionality')

    return dimensions

def is_in_tree(tree, Point):
    if tree.data is None:
        return False
    #print tree.data
    val1 = val2 = val3 = val4 = False
    if tree.data is not None:
        if ((Point[0] >= tree.data[0]) and (Point[0] <= tree.data[1]) and
            (Point[1] >= tree.data[2]) and (Point[1] <= tree.data[3])):
            return True
        
        if tree.axis == 0 or tree.axis == 2:
            if (Point[tree.axis/2] < tree.data[tree.axis]):
                val1 = is_in_tree(tree.left, Point)
            else:
                val2 = is_in_tree(tree.right, Point)
        else:
            val3 = is_in_tree(tree.left, Point)
            val4 = is_in_tree(tree.right, Point)
    return val1 or val2 or val3 or val4
        
class TreeSampleFilter:
    
    def __init__(self, Boundarys):
        self.tree = create(Boundarys)
    
    def is_normal(self, sample_point):
        return is_in_tree(self.tree, sample_point)

class SampleFilter:
    
    def __init__(self, Boundarys):
        self.boundarys = Boundarys
        
    def is_normal(self, sample_point):
        for x_lo, x_hi, y_lo, y_hi in self.boundarys:
            if (sample_point[0] >= x_lo and sample_point[0] <= x_hi
                and sample_point[1] >= y_lo and sample_point[1] <= y_hi):
                return True
        return False
                
    
if __name__ == "__main__":
    point1 = (1,2,1,2)
    point2 = (0,1,2,3)
    point3 = (1,2,3,4)
    point4 = (3,4,2,3)
    point5 = (1,2,2,3)
    point6 = (2,3,3,4)
    point7 = (3,4,2,3)
    point8 = (1,2,2,3)
    point9 = (2,3,3,4)
    points = zip(range(0,9),range(3,11),range(6,15))
    points = [point1, point2, point3, point4,point5,point6, point7,point8,point9]
    tree = create(points)
    
    #print is_in_tree(tree,Point=[0.4,1])
    #print is_in_tree(tree,Point=[1,1])
    
    TSF = TreeSampleFilter(points)
    print TSF.is_normal(sample_point = [0.4,1])
    print TSF.is_normal(sample_point = [1,1])
    print TSF.is_normal(sample_point = [1.5,2.5])
    
    SF = SampleFilter(points)
    print SF.is_normal(sample_point = [0.4,1])
    print SF.is_normal(sample_point = [1,1])
    print SF.is_normal(sample_point = [1.5,2.5])
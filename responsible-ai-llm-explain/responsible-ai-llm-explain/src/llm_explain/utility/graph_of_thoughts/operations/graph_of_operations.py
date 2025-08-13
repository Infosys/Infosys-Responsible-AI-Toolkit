'''
Copyright 2024 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies 
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE 
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from __future__ import annotations
from typing import List

from ..operations.operations import Operation


class GraphOfOperations:
    """
    Represents the Graph of Operations, which prescribes the execution plan of thought operations.
    """

    def __init__(self) -> None:
        """
        Initializes a new Graph of Operations instance with empty operations, roots, and leaves.
        The roots are the entry points in the graph with no predecessors.
        The leaves are the exit points in the graph with no successors.
        """
        self.operations: List[Operation] = []
        self.roots: List[Operation] = []
        self.leaves: List[Operation] = []

    def append_operation(self, operation: Operation) -> None:
        """
        Appends an operation to all leaves in the graph and updates the relationships.

        :param operation: The operation to append.
        :type operation: Operation
        """
        self.operations.append(operation)

        if len(self.roots) == 0:
            self.roots = [operation]
        else:
            for leave in self.leaves:
                leave.add_successor(operation)

        self.leaves = [operation]

    def add_operation(self, operation: Operation) -> None:
        """
        Add an operation to the graph considering its predecessors and successors.
        Adjust roots and leaves based on the added operation's position within the graph.

        :param operation: The operation to add.
        :type operation: Operation
        """
        self.operations.append(operation)
        if len(self.roots) == 0:
            self.roots = [operation]
            self.leaves = [operation]
            assert (
                len(operation.predecessors) == 0
            ), "First operation should have no predecessors"
        else:
            if len(operation.predecessors) == 0:
                self.roots.append(operation)
            for predecessor in operation.predecessors:
                if predecessor in self.leaves:
                    self.leaves.remove(predecessor)
            if len(operation.successors) == 0:
                self.leaves.append(operation)

from collections import OrderedDict
from typing import List, Dict, Set
from itertools import chain
from meta.formula import Formula, Variable
import sys


class ForceOrdering:
    COMPARATOR = lambda x: x[1]

    def __init__(self):
        self.dfsOrdering = DFSOrdering()

    def getOrder(self, formula: Formula) -> List[Variable]:
        originalVariables = sorted(
            set(chain(formula.variables(), formula.nnf().variables()))
        )
        cnf = formula.nnf().cnf()
        hypergraph = HypergraphGenerator.fromCNF(cnf)
        nodes = {node.content(): node for node in hypergraph.nodes()}
        ordering = self.force(cnf, hypergraph, nodes)
        ordering = [var for var in ordering if var in originalVariables]
        ordering.extend(var for var in originalVariables if var not in ordering)
        return ordering

    def force(
        self,
        formula: Formula,
        hypergraph: Hypergraph[Variable],
        nodes: Dict[Variable, HypergraphNode[Variable]],
    ) -> List[Variable]:
        initialOrdering = self.createInitialOrdering(formula, nodes)
        lastOrdering = None
        currentOrdering = initialOrdering
        while self.shouldProceed(lastOrdering, currentOrdering):
            lastOrdering = currentOrdering
            newLocations = {
                node: node.computeTentativeNewLocation(lastOrdering)
                for node in hypergraph.nodes()
            }
            currentOrdering = self.orderingFromTentativeNewLocations(newLocations)
        ordering = [None] * len(currentOrdering)
        for node, index in currentOrdering.items():
            ordering[index] = node.content()
        return ordering

    def createInitialOrdering(
        self, formula: Formula, nodes: Dict[Variable, HypergraphNode[Variable]]
    ) -> OrderedDict[HypergraphNode[Variable], int]:
        initialOrdering = OrderedDict()
        dfsOrder = self.dfsOrdering.getOrder(formula)
        for i, var in enumerate(dfsOrder):
            initialOrdering[nodes[var]] = i
        return initialOrdering

    def orderingFromTentativeNewLocations(
        self, newLocations: Dict[HypergraphNode[Variable], float]
    ) -> OrderedDict[HypergraphNode[Variable], int]:
        sortedNodes = sorted(newLocations.items(), key=self.COMPARATOR)
        ordering = OrderedDict()
        for i, (node, _) in enumerate(sortedNodes):
            ordering[node] = i
        return ordering

    def shouldProceed(
        self,
        lastOrdering: Dict[HypergraphNode[Variable], int],
        currentOrdering: Dict[HypergraphNode[Variable], int],
    ) -> bool:
        return lastOrdering != currentOrdering

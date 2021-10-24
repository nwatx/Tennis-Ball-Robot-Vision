import sys
import math
import random
from itertools import combinations
import gurobipy as gp
from gurobipy import GRB
import matplotlib.pyplot as plt

class TSPConst:
	def __init__(self) -> None:
		self.n = 0
# Callback - use lazy constraints to eliminate sub-tours

tspconst = TSPConst()

def subtourelim(model, where):
	if where == GRB.Callback.MIPSOL:
		# make a list of edges selected in the solution
		vals = model.cbGetSolution(model._vars)
		# print(model._vars.keys())
		selected = gp.tuplelist((i, j) for i, j in model._vars.keys()
								if vals[i, j] > 0.5)
		# find the shortest cycle in the selected edge list
		tour = subtour(selected, tspconst.n)
		if len(tour) < tspconst.n:
			# add subtour elimination constr. for every pair of cities in tour
			model.cbLazy(gp.quicksum(model._vars[i, j]
									 for i, j in combinations(tour, 2))
						 <= len(tour)-1)


# Given a tuplelist of edges, find the shortest subtour

def subtour(edges, n):
	unvisited = list(range(n))
	cycle = range(n+1)  # initial length has 1 more city
	while unvisited:  # true if list is non-empty
		thiscycle = []
		neighbors = unvisited
		while neighbors:
			current = neighbors[0]
			thiscycle.append(current)
			unvisited.remove(current)
			neighbors = [j for i, j in edges.select(current, '*')
						 if j in unvisited]
		if len(cycle) > len(thiscycle):
			cycle = thiscycle
	return cycle

# Parse argument

def solve(points, n):
	# Dictionary of Euclidean distance between each pair of points
	tspconst.n = n
	if n == 0:
		return []
	if n <= 2:
		return [x for x in range(0, n)]

	dist = {(i, j):
			math.sqrt(sum((points[i][k]-points[j][k])**2 for k in range(2)))
			for i in range(n) for j in range(i)}

	m = gp.Model()
	m.setParam('OutputFlag', False)
	m.Params.OutPutFlag = False

	# Create variables

	vars = m.addVars(dist.keys(), obj=dist, vtype=GRB.BINARY, name='e')
	m.addVar(n, obj=0, vtype=GRB.INTEGER, name='n')
	
	for i, j in vars.keys():
		vars[j, i] = vars[i, j]  # edge in opposite direction

	# You could use Python looping constructs and m.addVar() to create
	# these decision variables instead.  The following would be equivalent
	# to the preceding m.addVars() call...
	#
	# vars = tupledict()
	# for i,j in dist.keys():
	#   vars[i,j] = m.addVar(obj=dist[i,j], vtype=GRB.BINARY,
	#                        name='e[%d,%d]'%(i,j))

	# Add degree-2 constraint

	m.addConstrs(vars.sum(i, '*') == 2 for i in range(n))

	# Using Python looping constructs, the preceding would be...
	#
	# for i in range(n):
	#   m.addConstr(sum(vars[i,j] for j in range(n)) == 2)

	# Optimize model

	m._vars = vars
	m.Params.lazyConstraints = 1
	m.optimize(subtourelim)

	vals = m.getAttr('x', vars)
	selected = gp.tuplelist((i, j) for i, j in vals.keys() if vals[i, j] > 0.5)

	tour = subtour(selected, n)

	print('')
	print('Optimal tour: %s' % str(tour))
	print('Optimal cost: %g' % m.objVal)
	print('')

	# plt.plot([p[0] for p in points], [p[1] for p in points], 'ro')
	# for i in range(len(tour)):
	# 	j = (i + 1) % len(tour)
	# 	# plt.plot([points[tour[i]][0], points[tour[j]][0]])
	# 	plt.plot([points[tour[i]][0], points[tour[j]][0]], [points[tour[i]][1], points[tour[j]][1]])
	# plt.show()
	return tour

solve(points=[(49, 366), (145, 368)], n=2)
#!/usr/bin/python3

from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))




import time
import numpy as np
from TSPClasses import *
import heapq
import itertools
import heapq
import random


class TSPSolver:
	def __init__( self, gui_view ):
		self._scenario = None

	def setupWithScenario( self, scenario ):
		self._scenario = scenario


	''' <summary>
		This is the entry point for the default solver
		which just finds a valid random tour.  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of solution, 
		time spent to find solution, number of permutations tried during search, the 
		solution found, and three null values for fields not used for this 
		algorithm</returns> 
	'''
	
	def defaultRandomTour( self, time_allowance=60.0 ):
		results = {}
		cities = self._scenario.getCities()
		ncities = len(cities)
		foundTour = False
		count = 0
		bssf = None
		start_time = time.time()
		while not foundTour and time.time()-start_time < time_allowance:
			# create a random permutation
			perm = np.random.permutation( ncities )
			route = []
			# Now build the route using the random permutation
			for i in range( ncities ):
				route.append( cities[ perm[i] ] )
			bssf = TSPSolution(route)
			count += 1
			if bssf.cost < np.inf:
				# Found a valid route
				foundTour = True
		end_time = time.time()
		results['cost'] = bssf.cost if foundTour else math.inf
		results['time'] = end_time - start_time
		results['count'] = count
		results['soln'] = bssf
		results['max'] = None
		results['total'] = None
		results['pruned'] = None
		return results


	''' <summary>
		This is the entry point for the greedy solver, which you must implement for 
		the group project (but it is probably a good idea to just do it for the branch-and
		bound project as a way to get your feet wet).  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number of solutions found, the best
		solution found, and three null values for fields not used for this 
		algorithm</returns> 
	'''

	def greedy( self,time_allowance=60.0 ):
		pass
		
	def divideAndConquer( self, time_allowance=60 ):
		results = {}
		cities = self._scenario.getCities()
		start_time = time.time()
		sortedCities = 	sorted(cities, key=lambda city: city._x)
		bssf = self.divideAndConquerRec(sortedCities)
		if bssf.cost == float('inf'):
			sortedCities = sorted(cities, key=lambda city: city._y)
			bssf = self.divideAndConquerRec(sortedCities)
			if bssf.cost == float('inf'):
				while time.time()-start_time < time_allowance:
					random.shuffle(sortedCities)
					bssf = self.divideAndConquerRec(sortedCities)
					if bssf.cost < float('inf'):
						break
		end_time = time.time()
		print(bssf.route)
		results['cost'] = bssf.cost
		results['time'] = end_time - start_time
		results['count'] = 0
		results['soln'] = bssf
		results['max'] = None
		results['total'] = None
		results['pruned'] = None
		return results

	def divideAndConquerRec( self, cities ):
		numCities = len(cities)
		if numCities == 1:
			return TSPSolution(cities)

		firstCities = self.divideAndConquerRec(cities[:numCities//2])
		secondCities = self.divideAndConquerRec(cities[numCities//2:])
		return self.combineCities(firstCities, secondCities)	
		

	def combineCities(self, firstCities, secondCities):
		bestRoute = []
		firstCitiesArr = firstCities.route
		secondCitiesArr = secondCities.route
		bestRoute = TSPSolution(firstCitiesArr + secondCitiesArr)
		bestCost = bestRoute.cost
		for i in range(len(firstCitiesArr)):
			for j in range(len(secondCitiesArr)):
				tempRoute = firstCitiesArr[:i]
				tempRoute += secondCitiesArr[j:]
				tempRoute += secondCitiesArr[:j]
				tempRoute += firstCitiesArr[i:]
				tempSol = TSPSolution(tempRoute)
				if tempSol.cost < bestCost:
					bestCost = tempSol.cost
					bestRoute = tempSol
		return bestRoute

	def branchAndBound(self, time_allowance=60.0):
		results = {}
		cities = self._scenario.getCities()
		ncities = len(cities)
		foundTour = False
		count = 1
		max_queue = 0
		num_pruned = 0
		total_states = 0
		start_time = time.time()

		# Create initial bssf from random tour
		# This is space complexity O(n) and time complexity O(n)
		temp_bssf = self.defaultRandomTour().get('soln')
		self.bssf = self.CostObj(temp_bssf.cost, [], [], temp_bssf.route, 0)

		# Create first cost matrix
		# This is space and time complexity O(n^2)
		self.init_cost = np.zeros((ncities, ncities))
		for i in range(ncities):
			for j in range(ncities):
				if i == j:
					self.init_cost[i,j] = np.inf
					continue
				self.init_cost[i,j] = cities[i].costTo(cities[j])
		cur_path = [cities[0]._name]
		cur_city = [cities[0]]
		first_obj = self._reduceMatrix(self.CostObj(0, self.init_cost, [], [], 0), 0, True)
		self.init_cost = first_obj._matrix.copy()
		self.min_heap = [first_obj]
		heapq.heapify(self.min_heap)

		# Branch and bound to find path
		# This is space O(n^2) and time 
		while time.time()-start_time < time_allowance:
			if len(self.min_heap) == 0:
				break
			if len(self.min_heap) > max_queue:
				max_queue = len(self.min_heap)
			# Popping from heap is O(nlogn)
			cur_obj = heapq.heappop(self.min_heap)
			for i in range(len(cities)):
				# If city already visted skip it
				if i in cur_obj._path:
					continue
				
				# If path is available create reduced matrix
				if self.init_cost[cur_obj._index, i] != np.inf:
					total_states += 1
					red_obj = self._reduceMatrix(cur_obj, i)

					# If the cost is below the current bssf add to heap
					# else prune it
					if red_obj._cost < self.bssf._cost:
						# Pushing to heap is O(nlogn)
						heapq.heappush(self.min_heap, red_obj)

						# If the current node is a full cycle set it as new bssf
						if len(red_obj._path) == ncities:
							count += 1
							self.bssf = self.CostObj(red_obj._cost, red_obj._matrix.copy(), red_obj._path.copy(), 
													 red_obj._city_path.copy(), red_obj._index)
					else:
						num_pruned += 1
		end_time = time.time()


		results['cost'] = self.bssf._cost if self.bssf is not None else np.inf
		results['time'] = end_time - start_time
		results['count'] = count
		results['soln'] = TSPSolution(self.bssf._city_path)
		results['max'] = max_queue
		results['total'] = total_states
		results['pruned'] = num_pruned

		return results


	# Function for reducing cost matrix
	# This is space and time O(n^2)
	def _reduceMatrix( self, cur_obj, dest, first=False ):
		matrix = cur_obj._matrix.copy()
		cost = cur_obj._matrix.copy()
		a = cur_obj._index
		b = dest
		reduction_cost = 0

		# If not the first matrix set rows and postions to infinity and 
		# add the parent cost to the cost to travel to that postion
		if not first:
			matrix[a,b] = np.inf
			matrix[b,a] = np.inf
			matrix[a] = np.inf
			matrix[:,b] = np.inf
			reduction_cost += cur_obj._cost
			reduction_cost += cost[cur_obj._index,dest]

		# Determine the minimum in each row and then each column to reduce
		# matrtix and add the reduction total to the cost
		for i in range(len(matrix)):
			min_row = matrix[i].min()
			if min_row != np.inf:
				reduction_cost += min_row
				matrix[i] = matrix[i] - min_row
		for i in range(len(matrix)):
			min_col = matrix[:,i].min()
			if min_col != np.inf:
				reduction_cost += min_col
				matrix[:,i] = matrix[:,i] - min_col

		path = cur_obj._path.copy()
		path.append(dest)
		city_path = cur_obj._city_path.copy()
		city_path.append(self._scenario.getCities()[dest])
		return self.CostObj(reduction_cost, matrix, path, city_path, dest)


	def fancy( self,time_allowance=60.0 ):
		pass
		

	# Object to organize the data needed
	class CostObj:

		def __init__( self, cost, matrix, path, city_path, index ):
			self._matrix = matrix
			self._cost = cost
			self._path = path
			self._city_path = city_path
			self._index = index

		def __lt__( self, cmp):
			if len(self._path) > len(cmp._path):
				return True
			if len(self._path) == len(cmp._path) and self._cost < cmp._cost:
				return True
			return False

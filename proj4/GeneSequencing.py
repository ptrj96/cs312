#!/usr/bin/python3

from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import math
import time
import random

# Used to compute the bandwidth for banded version
MAXINDELS = 3

# Used to implement Needleman-Wunsch scoring
MATCH = -3
INDEL = 5
SUB = 1

class GeneSequencing:

	def __init__( self ):
		pass

	def align( self, seq1, seq2, banded, align_length):
		self.banded = banded
		self.MaxCharactersToAlign = align_length
		
		score = 0
		alignment1 = ''
		alignment2 = ''

		if banded:
			score, alignment2, alignment1 = self._banded_allign(seq1, seq2, align_length)
		else:
			score, alignment1, alignment2 = self._full_allign(seq1, seq2, align_length)
		
		return {'align_cost':score, 'seqi_first100':alignment1, 'seqj_first100':alignment2}

	def _banded_allign(self, seq1, seq2, align_length):

		# Set length to the align length if necessary
		seq1_len = align_length + 1 if len(seq1) > align_length else len(seq1) + 1
		seq2_len = align_length + 1 if len(seq2) > align_length else len(seq2) + 1
		seq1 = seq1[:seq1_len-1]
		seq2 = seq2[:seq2_len-1]

		# Return if there is a large difference in lengths
		if abs(seq1_len - seq2_len) > 3:
			return math.inf, 'Can not align', 'Can not align'

		# Initialize the scoring and path matrix to be n*k
		scoring_matrix = [[None for i in range(7)] for j in range(seq1_len)]
		path_matrix = [[None for i in range(7)] for j in range(seq1_len)]
		scoring_matrix[0][0] = 0

		# Populate the scoring and path matrix
		# This operation is space and time O(n*k) where n is
		# the length of seq1 and k is the window for banding
		for i in range(seq1_len):
			
			# Set the window for each row i of the second sequence
			seq2_win = ''
			if i < 4:
				seq2_win = '_' + seq2[:7]
			else:
				try:
					seq2_win = seq2[i-3-1:7+(i-3)]
				except:
					seq2_win = seq2[i-3-1:]

			for j in range(7): 
				seq1_char = seq1[i-1]
				seq2_char = ''
				if j >= len(seq2_win):
					continue
				else:
					seq2_char = seq2_win[j]
				left = 0
				top = 0
				diag = 0

				# This fills out the scoring and path matrix
				if i < 4:
					if i == 0:
						scoring_matrix[i][j] = INDEL*j
						path_matrix[i][j] = 'L'
						continue
					if j == 0:
						scoring_matrix[i][j] = INDEL*i
						path_matrix[i][j] = 'T'
						continue

					diag = scoring_matrix[i-1][j-1]
					top = scoring_matrix[i-1][j]
					left = scoring_matrix[i][j-1]
				elif j == 6:
					left = scoring_matrix[i][j-1]
					diag = scoring_matrix[i-1][j]
					top = float('inf')
				elif j == 0:
					left = float('inf')
					diag = scoring_matrix[i-1][j]
					top = scoring_matrix[i-1][j+1]
				else:
					left = scoring_matrix[i][j-1]
					top = scoring_matrix[i-1][j+1]
					diag = scoring_matrix[i-1][j]

				left_miss = left + INDEL
				top_miss = top + INDEL
				diag = diag + SUB if seq1_char != seq2_char else diag + MATCH

				if left_miss <= diag and left_miss <= top_miss:
					scoring_matrix[i][j] = left_miss
					path_matrix[i][j] = 'L'
				elif top_miss <= diag and top_miss <= left_miss:
					scoring_matrix[i][j] = top_miss
					path_matrix[i][j] = 'T'
				else:
					scoring_matrix[i][j] = diag
					path_matrix[i][j] = 'D'

		path_matrix[0][0] = 'S'

		for x in scoring_matrix[-1]:
			if x != None:
				score = x
		
		# This backtracks through the path matrix to 
		# make the alignments
		i = align_length if len(seq1) > align_length else len(seq1)
		j = 0

		while path_matrix[i][j] != None:
			j+=1
		j -= 1
		align_1 = []
		align_2 = []

		while path_matrix[i][j] != 'S':
			seq2_win = ''
			if i < 4:
				seq2_win = '_' + seq2[:7]
				if path_matrix[i][j] == 'D':
					align_1.append(seq1[i-1])
					align_2.append(seq2_win[j])
					i -= 1
					j -= 1
				elif path_matrix[i][j] == 'L':
					align_1.append(seq1[i-1])
					align_2.append('-')
					j -= 1
				else:
					align_2.append(seq2_win[j])
					align_1.append('-')
					i -= 1

			else:
				try:
					seq2_win = seq2[i-3-1:7+(i-3)]
				except:
					seq2_win = seq2[i-3-1:]
				if path_matrix[i][j] == 'D':
					align_1.append(seq1[i-1])
					align_2.append(seq2_win[j])
					i -= 1
				elif path_matrix[i][j] == 'L':
					align_1.append(seq1[i-1])
					align_2.append('-')
					j -= 1
				else:
					align_2.append(seq2_win[j])
					align_1.append('-')
					i -= 1
					j += 1
		

		return_len1 = -101 if len(seq1) > 100 else -(len(align_1) +1)
		return_len2 = -101 if len(seq2) > 100 else -(len(align_2) +1)

		return score, ''.join(align_1[:return_len1:-1]), ''.join(align_2[:return_len2:-1])

	def _full_allign(self, seq1, seq2, align_length):
		seq1_len = align_length + 1 if len(seq1) > align_length else len(seq1) + 1
		seq2_len = align_length + 1 if len(seq2) > align_length else len(seq2) + 1

		scoring_matrix = [[None for i in range(seq1_len)] for j in range(seq2_len)]
		path_matrix = [[None for i in range(seq1_len)] for j in range(seq2_len)]
		scoring_matrix[0][0] = 0

		# Populate the scoring and path matrix
		# This operation is space and time O(n*m) where n is
		# the length of seq1 and m is the lenght of seq2
		for i in range(seq2_len):
			for j in range(seq1_len):

				# This fills out the scoring and path matrix
				if i == 0:
					scoring_matrix[i][j] = INDEL*j
					path_matrix[i][j] = 'L'
					continue
				if j == 0:
					scoring_matrix[i][j] = INDEL*i
					path_matrix[i][j] = 'T'
					continue
				
				seq1_char = seq1[j-1]
				seq2_char = seq2[i-1]
				left = scoring_matrix[i][j-1]
				diag = scoring_matrix[i-1][j-1]
				top = scoring_matrix[i-1][j]

				left_miss = left + INDEL
				top_miss = top + INDEL
				diag = diag + SUB if seq1_char != seq2_char else diag + MATCH

				if left_miss <= diag and left_miss <= top_miss:
					scoring_matrix[i][j] = left_miss
					path_matrix[i][j] = 'L'
				elif top_miss <= diag and top_miss <= left_miss:
					scoring_matrix[i][j] = top_miss
					path_matrix[i][j] = 'T'
				else:
					scoring_matrix[i][j] = diag
					path_matrix[i][j] = 'D'
		path_matrix[0][0] = 'S'

		score = scoring_matrix[-1][-1]

		# This backtracks through the path matrix to find the 
		# alignments 
		i = align_length if len(seq1) > align_length else len(seq1)
		j = align_length if len(seq2) > align_length else len(seq2)
		align_1 = []
		align_2 = []

		while path_matrix[j][i] != 'S':
			if path_matrix[j][i] == 'D':
				align_1.append(seq1[i-1])
				align_2.append(seq2[j-1])
				i -= 1
				j -= 1
			elif path_matrix[j][i] == 'L':
				align_1.append(seq1[i-1])
				align_2.append('-')
				i -= 1
			else:
				align_2.append(seq2[j-1])
				align_1.append('-')
				j -= 1
		
		return_len1 = -101 if len(seq1) > 100 else -(len(seq1) +1)
		return_len2 = -101 if len(seq2) > 100 else -(len(seq2) +1)
		return score, ''.join(align_1[:return_len1:-1]), ''.join(align_2[:return_len2:-1])
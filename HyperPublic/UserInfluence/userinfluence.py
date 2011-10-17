#!/bin/python

import sys

user_map = {}
influence_map = {}

def add_to_map(user_str):
		length = len(user_str)
		u_added = []
		try:
				l_id = 0
				while True:
						f_id = user_str.index('X') + 1
						user_str = user_str[f_id:]
						f_id += l_id
						l_id = f_id
						u_added.append(f_id)
		except ValueError:
				u_id = len(user_map) + 1
				user_map[u_id] = u_added
				return

def calculate_influence():
		for k,v in user_map.iteritems():
				if v != [] and k not in influence_map:
						influence = indirect_influence(k)
						influence_map[k] = influence

def indirect_influence(u_id):
		u_influence = len(user_map[u_id])
		for f in list(user_map[u_id]):
				f_influence = 0
				if f not in influence_map:
						f_influence = indirect_influence(f)
						if f_influence:
								influence_map[f] = f_influence
				else:
						f_influence = influence_map[f]
				u_influence += f_influence
		return u_influence

def top3():
		sorted_scores = sorted(influence_map.values(), reverse=True)
		top3 = sorted_scores[:3]
		print repr(top3[0]) + repr(top3[1]) + repr(top3[2])

if __name__ == '__main__':
		filename = sys.argv[1]
		input_file = open(filename, 'r')
		while True:
				user_str = input_file.readline()
				if user_str == '':
						break
				add_to_map(user_str)

		calculate_influence()
		top3()


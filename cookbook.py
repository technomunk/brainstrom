# A general purpose utility for hierarchical recipe manipulation.
#
# A recipe is a general blueprint how to make a thing and consists of:
# - name (string): the name of the item
# - rate (number): abstract quantity the recipe produces
# - producer (string): the name of the station where the recipe is cooked
# - ingredients ([(number, string)]): list of tuples of rates and names of ingredients
#
# The implementation assumes that the rates are linear, so to
# make 2x recipe it is sufficient to use 2x ingredients.
#
# Example usage:
# json_string = '''
# [
#	{ name: "Dough", rate: 2, producer: "Mixer", ingredients: [ { name: "Flour", rate: 2 }, { name: "Water", rate: 1 }] }
# ]
#'''
# import Cookbook from cookbook
# cookbook = Cookbook(json.loads(json_string))
# cookbook.cook('Dough')

from collections import UserDict
from fractions import Fraction
from functools import reduce
from math import lcm

class Recipe():
	def __init__(self, name: str, rate: Fraction, producer: str, ingredients):
		self.name = name
		if isinstance(rate, Fraction):
			self.rate = rate
		else:
			self.rate = Fraction(rate)
		self.producer = producer
		self.ingredients = [(ingredient['rate'], ingredient['name']) for ingredient in ingredients]
	
	def __repr__(self):
		return f'{self.name}@{self.producer}'


class Cookbook(UserDict):
	def __init__(self, recipes: list = []):
		'''
		Initialize the cookbook with the list of provided recipes.
		'''
		super().__init__()
		for recipe in recipes:
			self.add(recipe)


	def add(self, recipe: Recipe):
		'''
		Add the given recipe to the cookbook
		'''
		if not isinstance(recipe, Recipe):
			recipe = Recipe(**recipe)
		self[recipe.name] = recipe
	

	def tree(self, name, rate = 1, depth = -1):
		'''
		Get the production tree of the provided item up to provided depth.
		'''
		if name not in self:
			raise KeyError(f"'{name}' is not a known recipe!")
		
		recipe = self[name]
		subtree = []
		if not isinstance(rate, Fraction):
			rate = Fraction(rate)
		for (ingredient_rate, ingredient_name) in recipe.ingredients:
			normalized_rate = ingredient_rate / recipe.rate * rate
			if depth != 0 and ingredient_name in self:
				subtree.append(self.tree(ingredient_name, normalized_rate, depth - 1))
			else:
				subtree.append((normalized_rate, ingredient_name))

		return {
			'name': name,
			'rate': rate,
			'producers': (rate / recipe.rate, recipe.producer),
			'subtree': subtree,
		}


def producers(tree):
	'''
	Get all the producers of a Cookbook.tree().
	'''
	def r_producers(tree, acc):
		if 'producers' in tree:
			(ratio, producer) = tree['producers']
			acc.append((ratio, producer, tree['name']))
			for subtree in tree['subtree']:
				r_producers(subtree, acc)
	
	result = []
	r_producers(tree, result)
	return result


def beautify_producer(tuple_producer):
	'''
	Create a nicer string representation for a producer tuple.
	'''
	(ratio, producer, item) = tuple_producer
	return f'{item}@({ratio.numerator}/{ratio.denominator}){producer}'


def merge_producers(producers):
	'''
	Merge producers producing the same items together.
	'''
	result = dict()
	for (ratio, producer, item) in producers:
		if (producer, item) in result:
			result[(producer, item)] += ratio
		else:
			result[(producer, item)] = ratio
	return result


def producer_lcm(producers):
	'''
	Find least common multiple of provided producers.
	'''
	if isinstance(producers, list):
		producers = merge_producers(producers)

	return reduce(lambda acc, ratio: lcm(acc, ratio.denominator), producers.values(), 1)

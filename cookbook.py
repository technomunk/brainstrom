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
from sys import stdout

def __expect_type(var, type):
	if not isinstance(var, type):
		raise TypeError()


def __expect_types(var, *args):
	for typ in args:
		if isinstance(var, typ):
			return
	raise TypeError()


def beautify_ratio(ratio: Fraction):
	if ratio.denominator == 1:
		return str(ratio.numerator)
	else:
		return f'({ratio.numerator}/{ratio.denominator})'


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

		return RecipeTree(recipe, rate, subtree)
	

	def __repr__(self):
		mid = ''.join([f'{recipe}, ' for recipe in self.values()])
		return f'Cookbook{{ {mid} }}'


# TODO: add an iterator to the tree
class RecipeTree():
	def __init__(self, recipe: Recipe, rate: Fraction, subtree: list):
		self.recipe = recipe
		self.rate = rate
		self.subtree = subtree
	
	def print(self, out = stdout, indent = '\t'):
		def r_print(node: RecipeTree, out, indent: str, depth: int):
			normalized_rate = node.rate / node.recipe.rate
			out.write(f"{indent * depth}{beautify_ratio(node.rate)}x'{node.recipe.name}' @ {beautify_ratio(normalized_rate)}x'{node.recipe.producer}':\n")
			for tree in node.subtree:
				if isinstance(tree, RecipeTree):
					r_print(tree, out, indent, depth + 1)
				else:
					(rate, item) = tree
					out.write(f"{indent * (depth + 1)}{beautify_ratio(rate)}x'{item}'\n")
		r_print(self, out, indent, 0)

	def __repr__(self):
		normalized_rate = self.rate / self.recipe.rate
		return f"{beautify_ratio(self.rate)}x'{self.recipe.name}' @ {beautify_ratio(normalized_rate)}x'{self.recipe.producer}' : {self.subtree}"
	
	def __mul__(self, num):
		if not isinstance(num, Fraction):
			num = Fraction(num)
		def mul(node, num):
			if isinstance(node, RecipeTree):
				return node * num
			else:
				return (node[0] * num, node[1])
		subtree = [mul(node, num) for node in self.subtree]
		return RecipeTree(self.recipe, self.rate * num, subtree)
	
	def lcm(self):
		'''
		Find the least common whole multiple of all the parts of the recipe tree.
		If the tree is multiplied by the result of this, all components will occupy 100%
		of their producers.
		'''
		def _lcm(num, node):
			if isinstance(node, RecipeTree):
				return lcm(node.lcm(), num)
			else:
				return lcm(node[0].denominator, num)
		
		return reduce(_lcm, self.subtree, (self.rate / self.recipe.rate).denominator)

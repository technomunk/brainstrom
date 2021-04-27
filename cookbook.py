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

class Recipe():
	def __init__(self, name: str, rate: float, producer: str, ingredients):
		self.name = name
		self.rate = rate
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
		if recipe is not Recipe:
			recipe = Recipe(**recipe)
		self[recipe.name] = recipe
	
	def ingredients(self, name, limit = 0):
		'''
		Find the ingredients to make the provided item. If limit is set, the ingredients
		of ingredients will be recursively gathered until the limit is reached.
		Returns [(rate, name)] of the ingredients to make 1 rate of the requested recipe.
		'''
		if name not in self:
			raise KeyError(f"'{name}' is not a known recipe!")
		
		recipe = self[name]
		result = []
		for (ingredient_rate, ingredient_name) in recipe.ingredients:
			normalized_rate = ingredient_rate / recipe.rate
			if limit > 0 and ingredient_name in self:
				subingredients = self.ingredients(ingredient_name, limit - 1)
				result.extend([(rate * normalized_rate, name) for (rate, name) in subingredients])
			else:
				result.append((normalized_rate, ingredient_name))

		return result
	
	def producers(self, ingredients):
		'''
		Find the number of producers required to produce the provided ingredients in correct rates.
		'''
		result = []
		for (rate, name) in ingredients:
			if name in self:
				recipe = self[name]
				result.append((recipe.rate / rate, f'{recipe.producer}=>{name}'))
			else:
				result.append((rate, name))

		return result

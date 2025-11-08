"""
Lab 3.2 – Comprehensions and Transformations

Goals:
- Practice list, set, and dictionary comprehensions.
- Transform and filter data concisely.

Instructions:
Given the list:
    numbers = [3, 8, -2, 7, 0, -5, 10]

1. Create a list `squares` with the square of each number.
2. Create a list `positives` containing only positive numbers.
3. Create a set `even_squares` of the squares of even numbers.
4. Create a dictionary `cubes` mapping each number to its cube.
5. Print all results.
"""

# Step 1: Data
numbers = [3, 8, -2, 7, 0, -5, 10]

# Step 2: Comprehensions
squares = [n**2 for n in numbers]  # every number squared
positives = [n for n in numbers if n > 0]  # only positives
even_squares = {n**2 for n in numbers if n % 2 == 0}  # set of even-number squares
cubes = {n: n**3 for n in numbers}  # dictionary number→cube

# Step 3: Print results
print("Numbers:", numbers)
print("Squares:", squares)
print("Positives:", positives)
print("Even squares:", even_squares)
print("Cubes:", cubes)

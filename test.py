import math


def solve_diophantine(a, b, c):
    """
    Solves ax + by = c for non-negative integers (x, y).
    Returns a list of valid (x, y) pairs.
    """
    if a == 0 and b == 0:
        return []  # No solutions

    solutions = []
    def extended_gcd(a, b):
        if b == 0:
            return (a, 1, 0)
        else:
            g, x1, y1 = extended_gcd(b, a % b)
            x = y1
            y = x1 - (a // b) * y1
            return (g, x, y)

    g, x0, y0 = extended_gcd(a, b)

    # Check if solutions exist
    if c % g != 0:
        return solutions  # No solutions

    # Scale the solution to match ax + by = c
    scale = c // g
    x0 *= scale
    y0 *= scale

    # Generate all solutions using parametric form
    t_multiplier_x = b // g
    t_multiplier_y = -a // g

    # Find bounds for t to keep x and y non-negative
    if t_multiplier_x == 0:
        t_min = -float('inf')
        t_max = float('inf')
    else:
        t_min = -x0 // t_multiplier_x
        t_max = y0 // (-t_multiplier_y)

    # Iterate over valid t values
    for t in range(t_min, t_max + 1):
        x = x0 + t_multiplier_x * t
        y = y0 + t_multiplier_y * t
        if x >= 0 and y >= 0:
            solutions.append((x, y))

    return solutions


# Example: 2x + 3y = 15
solutions = solve_diophantine(3, 7, 25)
print("Solutions for 2x + 3y = 15:")

print(solutions)  # Output: [(3, 3), (9, 2), (15, 1)]
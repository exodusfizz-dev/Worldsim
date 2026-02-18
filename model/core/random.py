'''Helper functions related to randomness'''
import math

def _sample_normal(expected, rng) -> int:
    '''Samples a count based on normal distribution around expected count. 
    Uses numpy normal (gaussian) distribution.'''
    if expected > 0:
        stddev = math.sqrt(expected)
    else:
        return 0
    sample = rng.normal(loc=expected, scale=stddev)
    return max(0, int(sample))

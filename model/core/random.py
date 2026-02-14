import math

def _sample_normal(expected, rng):
    '''Samples a count based on normal distribution around expected count. Uses numpy normal distribution.'''
    if expected > 0:
        stddev = math.sqrt(expected)
    else:
        return 0
    sample = rng.normal(loc=expected, scale=stddev)
    return max(0, int(sample))

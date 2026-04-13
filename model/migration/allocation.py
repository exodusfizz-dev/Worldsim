"""Population draw and transfer allocation helpers."""


class MigrationAllocator:
    """Draw migration counts and split allocation targets."""

    def __init__(self, rng) -> None:
        self.rng = rng

    def draw_count(self, population: int, probability: float) -> int:
        """Draw integer migrants using RNG binomial when available."""
        n = max(int(population), 0)
        p = max(min(probability, 1.0), 0.0)
        if n == 0 or p <= 0:
            return 0

        if self.rng is not None and hasattr(self.rng, "binomial"):
            return min(int(self.rng.binomial(n, p)), n)
        return int(round(n * p))

    def fallback_split(self, amount: int, destination_sizes: list[int | object]) -> list[tuple[int, int]]:
        """Split integer amount across destination groups by size share."""
        # TODO: Evaluate whether split should be even, and if it makes sense to have it across all groups.
        if amount <= 0:
            return []

        sizes = []
        for dest in destination_sizes:
            if hasattr(dest, "size"):
                sizes.append(max(int(dest.size), 0))
            else:
                sizes.append(max(int(dest), 0))

        if not sizes:
            return []

        total_size = sum(sizes)
        if total_size <= 0:
            base = amount // len(sizes)
            rem = amount % len(sizes)
            out = [(idx, base) for idx in range(len(sizes))]
            for idx in range(rem):
                out[idx] = (out[idx][0], out[idx][1] + 1)
            return out

        alloc: list[int] = []
        remainders: list[tuple[int, float]] = []
        assigned = 0
        for idx, size in enumerate(sizes):
            exact = amount * (size / total_size)
            floor_val = int(exact)
            alloc.append(floor_val)
            assigned += floor_val
            remainders.append((idx, exact - floor_val))
        remainders.sort(key=lambda x: x[1], reverse=True)
        for i in range(amount - assigned):
            alloc[remainders[i][0]] += 1
        return [(idx, val) for idx, val in enumerate(alloc) if val > 0]

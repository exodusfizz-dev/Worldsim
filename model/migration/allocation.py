"""Population draw and transfer allocation helpers."""


class MigrationAllocator:
    """Draw migration counts and safely transfer populations."""

    def __init__(self, rng) -> None:
        self.rng = rng

    def draw_count(self, population: float, probability: float) -> int:
        """Draw integer migrants using RNG binomial when available."""
        n = max(int(population), 0)
        p = max(min(probability, 1.0), 0.0)
        if n == 0 or p <= 0:
            return 0

        if self.rng is not None and hasattr(self.rng, "binomial"):
            return int(self.rng.binomial(n, p))
        return int(round(n * p))

    def safe_transfer(self, source_group, target_group, requested_amount: int) -> int:
        """Move integer population safely between groups."""
        if requested_amount <= 0:
            return 0
        available = max(int(source_group.size), 0)
        moved = min(requested_amount, available)
        if moved <= 0:
            return 0
        source_group.size -= moved
        target_group.size += moved
        return moved

    def fallback_split(self, amount: int, destination_groups) -> list[tuple[int, int]]:
        """Split integer amount across destination groups by size share."""
        if amount <= 0 or not destination_groups:
            return []

        total_size = sum(max(int(group.size), 0) for group in destination_groups)
        if total_size <= 0:
            base = amount // len(destination_groups)
            rem = amount % len(destination_groups)
            out = [(idx, base) for idx in range(len(destination_groups))]
            for idx in range(rem):
                out[idx] = (out[idx][0], out[idx][1] + 1)
            return out

        alloc: list[int] = []
        remainders: list[tuple[int, float]] = []
        assigned = 0
        for idx, group in enumerate(destination_groups):
            exact = amount * (max(int(group.size), 0) / total_size)
            floor_val = int(exact)
            alloc.append(floor_val)
            assigned += floor_val
            remainders.append((idx, exact - floor_val))
        remainders.sort(key=lambda x: x[1], reverse=True)
        for i in range(amount - assigned):
            alloc[remainders[i][0]] += 1
        return [(idx, val) for idx, val in enumerate(alloc) if val > 0]

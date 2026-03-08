class PopulationGenerator:
    """Generate population groups based on city characteristics."""

    def __init__(self, rng, base_group_count: int = 5):
        """
        Args:
            rng: numpy random generator
            base_group_count: number of population groups per city (can vary by size)
        """
        self.rng = rng
        self.base_group_count = base_group_count

    def generate_for_city(self, city_name: str, population: int) -> list[dict]:
        """
        Generate population groups for a city.
        
        Customize the distribution, healthcare levels, etc. here.
        Returns list of group dicts suitable for PopulationGroup.from_dict()
        """
        if population > 1000000:
            group_count = max(1, self.base_group_count * (population // 1000000))
        else:
            group_count = max(1, self.base_group_count)
        base_size = population // group_count

        groups = []
        for _ in range(group_count):
            base_healthcare = max(0.3, min(0.95, 0.3 + (population / 1000000) * 0.6))
            healthcare = self.rng.uniform(
                max(0.2, base_healthcare - 0.2),
                min(0.99, base_healthcare + 0.2)
            )

            size_variance = self.rng.uniform(1.15, 1.9) - healthcare
            group_size = int(base_size * size_variance)

            groups.append({
                "size": group_size,
                "base_healthcare": healthcare,
                "healthcare_capacity": max(100, int(group_size * 0.1)),
            })

        return groups
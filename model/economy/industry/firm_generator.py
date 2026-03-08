class FirmGenerator:
    """Generate firms based on city/province characteristics."""

    # (productivity_per_worker, wage_multiplier, input_materials)
    INDUSTRY_TEMPLATES = {
        "food": (7.0, 1.0, None),
        "copper": (3.5, 1.2, "tools"),
        "cloth": (4.0, 1.1, None),
        "tools": (4.5, 1.3, "timber"),
        "timber": (5.0, 1.0, None),
    }

    # Relative demand for city labour by industry.
    INDUSTRY_WEIGHTS = {
        "food": 0.34,
        "cloth": 0.22,
        "timber": 0.18,
        "tools": 0.16,
        "copper": 0.10,
    }

    def __init__(self, rng, base_wage: float = 25.0):
        """
        Args:
            rng: numpy random generator
            base_wage: baseline wage (customize by era/region)
        """
        self.rng = rng
        self.base_wage = base_wage

    def generate_for_city(
        self,
        city_name: str,
        population: int,
        city_size_rank: float = 0.5,
    ) -> list[dict]:

        """Generate firms for a city."""
        firms = []

        city_workforce = max(1, int(population * 0.55))
        employment_target = max(100, int(city_workforce * (0.35 + 0.25 * city_size_rank)))

        industry_count = max(3, min(5, int(3 + city_size_rank * 2)))
        available = list(self.INDUSTRY_TEMPLATES.keys())
        chosen_industries = set(
            self.rng.choice(
                available,
                size=industry_count,
                replace=False,
            ).tolist()
        )
        # Guarantee at least one baseline sector that can produce without upstream inputs.
        chosen_industries.add("food")
        chosen_industries.add("cloth")
        chosen_industries = sorted(chosen_industries)

        total_weight = sum(self.INDUSTRY_WEIGHTS.get(good, 0.1) for good in chosen_industries)
        if total_weight <= 0:
            total_weight = 1.0

        for good in chosen_industries:
            prod, wage_mult, input_mats = self.INDUSTRY_TEMPLATES[good]
            weight = self.INDUSTRY_WEIGHTS.get(good, 0.1) / total_weight
            desired_workers = max(50, int(employment_target * weight))

            # Labour demand ~= production_capacity / productivity.
            capacity = int(desired_workers * prod * 1.15)
            wage = max(10, int(self.base_wage * wage_mult))

            # Provide multi-year wage runway so firms don't instantly collapse before markets mature.
            capital = int(max(desired_workers * wage * 120, capacity * 20))
            ownership = "state" # if good == "food" else (
                #"state" if self.rng.random() < 0.3 else "private"
            #)

            firms.append({
                "productivity": prod,
                "production_capacity": max(10000, capacity),
                "capital": max(10000, capital),
                "ownership": ownership,
                "wage": wage,
                "good": good,
                "input_mats": input_mats
            })

        return firms

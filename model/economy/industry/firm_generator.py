class FirmGenerator:
    """Generate firms based on city/province characteristics."""

    INDUSTRY_TEMPLATES = {
        "food": (17, 0.003, 1.0, "tools"),
        "copper": (0.14, 0.0001, 1.2, "tools"),
        "cloth": (0.5, 0.0002, 1.1, None),
        "tools": (0.3, 0.00015, 1.3, "timber"),
        "timber": (2.0, 0.0005, 1.0, "tools"),
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


        industry_count = max(2, min(5, int(2 + city_size_rank * 3)))
        chosen_industries = self.rng.choice(
            list(self.INDUSTRY_TEMPLATES.keys()),
            size=industry_count,
            replace=False,
        )

        for good in chosen_industries:
            prod, cap_per_capita, wage_mult, input_mats = self.INDUSTRY_TEMPLATES[good]

            capacity = int(population * cap_per_capita)
            capital = int(capacity * 25)
            ownership = "state" # if good == "food" else (
                #"state" if self.rng.random() < 0.3 else "private"
            #)

            firms.append({
                "productivity": prod,
                "production_capacity": max(10000, capacity),
                "capital": max(10000, capital),
                "ownership": ownership,
                "wage": max(10, int(self.base_wage * wage_mult)),
                "good": good,
                "input_mats": input_mats
            })

        return firms
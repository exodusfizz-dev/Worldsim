"""Simulation-wide invariant checks used by tests and debugging."""

import numpy as np


def collect_invariant_errors(core):
    errors = []
    for country in core.countries:
        for province in country.provinces:
            for city in province.cities:
                if city.inv.get("food", 0) < 0:
                    errors.append(f"{city.name}: negative food inventory")
                for good, amount in city.inv.items():
                    if amount < 0:
                        errors.append(f"{city.name}: negative inventory for {good}")

                groups = city.population.groups
                if np.any(groups["size"] < 0):
                    errors.append(f"{city.name}: negative group size")
                if np.any(groups["sick"] < 0):
                    errors.append(f"{city.name}: negative sick count")
                if np.any(groups["money"] < 0):
                    errors.append(f"{city.name}: negative group money")
                if np.any(groups["employed"] < 0):
                    errors.append(f"{city.name}: negative employed count")
                if np.any(groups["employed"] > groups["size"]):
                    errors.append(f"{city.name}: employed exceeds group size")

                for firm in city.firms:
                    good_inventory = firm.inv.get(firm.good, 0.0)
                    if good_inventory < 0:
                        errors.append(f"{city.name}: negative firm inventory for {firm.good}")
                    if firm.employed < 0:
                        errors.append(f"{city.name}: negative firm employment")
                    if firm.total_productivity < 0:
                        errors.append(f"{city.name}: negative firm productivity")
                    if firm.market_capital < 0:
                        errors.append(f"{city.name}: negative firm market capital")
                if city.state.treasury < 0:
                    errors.append(f"{city.name}: negative city treasury")
    return errors


def assert_core_invariants(core):
    errors = collect_invariant_errors(core)
    if errors:
        raise AssertionError("\n".join(errors))

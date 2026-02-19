'''
City.py handles city objects, owned by provinces.
'''
from dataclasses import dataclass, field
from statistics import mean
from model.migration import Migration
from model.city.city_data import CityData
from model.economy import LabourMarket

@dataclass
class CityParams:
    """Immutable construction parameters for a city."""

    name: str
    populations: list
    firms: list

@dataclass
class CityState:
    """Mutable city state updated during each simulation tick."""

    employed: int = 0
    migrations: list = field(default_factory=list)
    last_food_deficit: int = None
    migration_attractiveness: float = 1
    inv: dict = field(default_factory=dict)

class City:
    """City object owned by provinces."""

    def __init__(self, cfg: dict, rng, params: CityParams) -> None:
        self.p = params
        self.rng = rng
        self.cfg = cfg

        self.state = CityState()

        DEFAULT_MIGRATION_RATE = self.cfg['migration'].get('intergroup_rate', 0.0005)
        self.migration = Migration(rng=self.rng, migration_rate=DEFAULT_MIGRATION_RATE, obj=self)

        self.labour_market = LabourMarket(self.rng, country_policy = None)

        self.state.migration_attractiveness = mean(group.migration_attractiveness for group in self.p.populations)

        for firm in self.p.firms:
            self.state.inv.setdefault(firm.good, 0.0)
        if "food" not in self.state.inv:
            self.state.inv["food"] = 0.0

        self.city_data = CityData(self)

    @classmethod
    def from_dict(cls, city_data: dict, populations, firms, rng, cfg) -> "City":
        return cls(
            params=CityParams(
                name=city_data["name"],
                populations=populations,
                firms=firms,
            ),
            rng=rng,
            cfg=cfg,
        )

    @property
    def employed(self) -> int:
        return self.state.employed

    @property
    def migrations(self) -> list[GroupMigrationEvent]:
        return self.state.migrations

    @property
    def last_food_deficit(self) -> float | None:
        return self.state.last_food_deficit

    @property
    def inv(self) -> dict[str, float]:
        return self.state.inv

    @property
    def migration_attractiveness(self) -> float:
        return self.state.migration_attractiveness

    @migration_attractiveness.setter
    def migration_attractiveness(self, value: float) -> None:
        self.state.migration_attractiveness = value


    @property
    def name(self) -> str:
        return self.p.name

    @property
    def populations(self) -> list:
        return self.p.populations

    @property
    def firms(self) -> list:
        return self.p.firms


    def tick(self):
        for group in self.p.populations: # City controls tick updates of all owned population groups
            group.tick()
        self.state.migration_attractiveness = mean(
            group.migration_attractiveness for group in self.p.populations
            )

        self.state.employed = self.labour_market.clear_market(
            populations=self.p.populations,
            firms=self.p.firms,
        )

        for firm in self.p.firms:
            firm.tick()
            if firm.good not in self.state.inv:
                self.state.inv.setdefault(firm.good, 0.0)

            if firm.ownership == "state":
                self.state.inv[firm.good] += firm.transfer_to_city()

        self.consume_food()
        self.run_migrations() # Runs migrations between population groups
        self.city_data.update_city_data()



    def run_migrations(self):
        if self.cfg.get('migration', {}).get('enabled', True):
            self.state.migrations.append(self.migration.intergroup_migration())

    def consume_food(self) -> None:
        """Consume food and apply starvation effects when supply is insufficient."""
        food_needed = sum(g.compute_food_consumption() for g in self.p.populations)
        if food_needed < self.state.inv["food"]:
            self.state.inv["food"] -= food_needed
            self.state.last_food_deficit = None
            return

        self.state.last_food_deficit = food_needed - self.state.inv["food"]
        self.state.migration_attractiveness = 0.0
        self.state.inv["food"] = 0.0

        if not self.p.populations:
            return
        per_group_deficit = self.state.last_food_deficit // len(self.p.populations)
        for group in self.p.populations:
            group.starve(food_deficit=per_group_deficit)

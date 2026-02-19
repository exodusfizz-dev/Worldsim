from dataclasses import dataclass, field
from model.migration import Migration

@dataclass
class ProvinceParams:
    """Immutable construction parameters for a province."""

    name: str
    area: int
    cities: list


@dataclass
class ProvinceState:
    migrations: list = field(default_factory=list)

class Province:
    """Province object owning a list of cities."""

    def __init__(self, cfg: dict, rng, params: ProvinceParams) -> None:
        self.rng = rng
        self.cfg = cfg
        self.p = params
        self.state = ProvinceState()

        DEFAULT_MIGRATION_RATE = 0.002
        self.migration = Migration(rng=self.rng, migration_rate=DEFAULT_MIGRATION_RATE, obj=self)


    @classmethod
    def from_dict(cls, province_data: dict, cities, cfg, rng) -> "Province":
        return cls(
            params=ProvinceParams(
                name=province_data["name"],
                area=province_data["area"],
                cities=cities,
            ),
            cfg=cfg,
            rng=rng,
        )

    @property
    def name(self) -> str:
        return self.p.name

    @property
    def cities(self) -> list:
        return self.p.cities

    @property
    def area(self) -> int:
        return self.p.area

    @property
    def migrations(self):
        return self.state.migrations

    def tick(self) -> None:
        for city in self.p.cities:
            city.tick()
        self.run_migrations()


    def run_migrations(self):

        '''
        Handles migration between cities in the province.
        '''

        if self.cfg.get('migration', {}).get('enabled', True):

            pass
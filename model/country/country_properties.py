'''Property accessors for country obj.'''

from dataclasses import dataclass

@dataclass
class CountryParams:
    name: str
    provinces: list

@dataclass
class CountryProperties:
    @property
    def name(self):
        return self.p.name

    @property
    def provinces(self):
        return self.p.provinces

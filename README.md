# Worldsim

Worldsim is an experimental agent-based simulation that builds a simplified world from real geographic data. It loads countries, provinces and cities from Natural Earth data, generates population groups and firms, then advances the simulation in weekly ticks.

This project is discontinued and unfinished, but I am keeping it as a record of my first major Python project and the engineering lessons it gave me.

## What it simulates

- Countries, provinces and cities built from Natural Earth geographic datasets
- City population groups with healthcare, education, money, employment and sickness state
- Inter-city and inter-group migration with deterministic seeded runs
- Simple firm, labour, food and treasury systems
- Console reports, population graphs and optional map visualisation

## What I learned

This project taught me how to structure a larger Python codebase with modules, classes and tests. I also learned a lot about simulation design, reproducibility, geospatial data, profiling, and the trade-offs between adding features and maintaining code quality.

I stopped development because the project had grown too broad while my programming skills were improving quickly. Rather than continually rewriting old systems, I chose to leave Worldsim as a learning project and move on to smaller, more focused simulations.

## Running it

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Tests

```bash
python -m unittest
PROFILE_RUN=1 python -m unittest tests.test_profile_report -v
```

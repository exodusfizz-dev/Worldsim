CONFIG = {

    "seed":
        {"seed": 42,
         "use": True},

    "main":
        {"reporter":     # Controls reporting system; what is printed/saved and how often
            {"enabled": True,
            "report_interval": 25,
            "sub_province_report": True
            },
        "pop_graph":
            {"enabled": False,
            },
        "map_display":
            {"enabled": False,
            },
        },

    "city": 
        {"migration":
            {"enabled": True,
            "intergroup_rate": 0.0005, 
            # Default = 0.0005 = 0.05%
            },
        "economy":
            {"labour_tax_rate": 0.2,       # Income tax on employed workers
             "food_price": 5.0,             # Price per unit food (TODO: move to commodity market)
             },
        },

    "province":
        {"migration":
            {"enabled": True,
             "intercity_rate": 0.0001, 
            # Default = 0.0001 = 0.01%
            }
        },

    "country":
        {"_":
         {"enabled": True,
          }
        },

    "location":
        {"min_cities_per_province": 5,
         "province_collation_threshold": 5
        },
}

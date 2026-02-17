CONFIG = {

    "seed":
        {"seed": 42,
         "use": True}, # Random seed for later use

    "main":
        {"reporter":     # Controls reporting system; what is printed/saved and how often
            {"enabled": True,
            "report_interval": 6,
            "sub_province_report": True
            },
        "pop_graph":
            {"enabled": False,
            },
        },

    "city": 
        {"migration":
            {"enabled": True,
            "intergroup_rate": 0.0005, # Default = 0.0005 = 0.05%
            }
        },

    "province":
        {"migration":
            {"enabled": False,
             "intercity_rate": 0.0001, 
            # Default = 0.0001 = 0.01%
            }
        },

    "country":
        {"_":
         {"enabled": True,
          }
        },
}

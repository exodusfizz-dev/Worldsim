CONFIG = {
    
    "seed": 
        {"seed": 42,
         "use": True}, # Random seed for later use

    "main":
        {"reporter":     # Controls reporting system; what is printed/saved and how often
            {"enabled": True, 
            "report_interval": 6,
            }},
            

    "city": 
        {"migration": 
            {"enabled": True, 
            "intergroup_rate": 0.0005, # Decimal percentage of population migrating each tick. Default = 0.0005 = 0.05%
            }}, 
            
    "province": 
        {"migration": 
            {"enabled": False, 
             "intercity_rate": 0.0001, # Decimal percentage of population migrating between cities each tick. Default = 0.0001 = 0.01% 
            }},


}

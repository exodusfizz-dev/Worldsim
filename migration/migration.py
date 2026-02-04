class Migration:
    def __init__(self, rng, migration_rate):
        self.rng = rng
        self.migration_rate = migration_rate


    def migrate(self, source, potential_targets):
        """
        Migrate a portion of source to a target with better attractiveness.
        
        Args:
            source: Object with size and migration_attractiveness attributes
            potential_targets: List of objects that could receive migrants
        
        Returns:
            Tuple of (migrated_amount, target_object) or (0, None) if no migration
        """
        better_targets = [t for t in potential_targets 
                          if t.migration_attractiveness > source.migration_attractiveness]
        
        if not better_targets:
            return 0, None
        
        target = min(better_targets, key=lambda t: t.migration_attractiveness)
        
        migrated_amount = source.size * self.migration_rate
        source.size -= migrated_amount
        target.size += migrated_amount
        
        return migrated_amount, target
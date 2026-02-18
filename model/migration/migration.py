class Migration:
    def __init__(self, obj, rng, migration_rate):
        self.rng = rng
        self.migration_rate = migration_rate
        self.o = obj


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


    def intercity_migration(self):
        pass

    def intergroup_migration(self):
        migrations = []

        for i, group in enumerate(self.o.populations, 1):
            migrated_amount, target = self.migrate(group, self.o.populations)

            if migrated_amount > 0:
                target_index = self.o.populations.index(target) + 1

                migrations.append(i, group, target_index)

        return migrations

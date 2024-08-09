from sqlalchemy import create_engine

from lending.domain import lending


def setup_db():
    """Setup database schema"""
    with lending.domain_context():
        # Setup databases before running tests
        for _, provider in lending.providers.items():
            if provider.conn_info["provider"] in ("sqlite", "postgresql"):
                engine = create_engine(provider.conn_info["database_uri"])

                # Ensure live entities are loaded and registered with SQLAlchemy
                for _, aggregate_record in lending.registry.aggregates.items():
                    if aggregate_record.cls.meta_.provider == provider.name:
                        lending.repository_for(aggregate_record.cls)._dao

                for _, entity_record in lending.registry.entities.items():
                    if entity_record.cls.meta_.provider == provider.name:
                        lending.repository_for(entity_record.cls)._dao

                for _, entity_record in lending.registry.views.items():
                    if entity_record.cls.meta_.provider == provider.name:
                        lending.repository_for(entity_record.cls)._dao

                # Create RDBMS Tables
                provider._metadata.create_all(engine)


def drop_db():
    """Drop database schema"""
    with lending.domain_context():
        # Setup databases before running tests
        for _, provider in lending.providers.items():
            if provider.conn_info["provider"] in ("sqlite", "postgresql"):
                engine = create_engine(provider.conn_info["database_uri"])

                # Destroy databases after running tests
                provider._metadata.drop_all(engine)

from ez2erp_engine.models import BaseModel


class Organization(BaseModel):
    table_name = 'core_organizations'

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.description = kwargs.get('description')
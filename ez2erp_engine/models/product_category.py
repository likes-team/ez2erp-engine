from ez2erp_engine.models import BaseModel


class ProductCategory(BaseModel):
    table_name = 'inventory_product_categories'

    def __init__(self, **kwargs):
        super(ProductCategory, self).__init__(**kwargs)
        self.name = kwargs.get('name')
        self.description = kwargs.get('description')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

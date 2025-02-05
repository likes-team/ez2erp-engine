from ez2erp_engine.models import BaseModel


class Product(BaseModel):
    table_name = 'inventory_products'

    def __init__(self, **kwargs):
        super(Product, self).__init__(**kwargs)
        self.name = kwargs.get('name')
        self.cost_price = kwargs.get('cost_price')
        self.sale_price = kwargs.get('sale_price')
        self.product_type = kwargs.get('product_type')
        self.category_id = kwargs.get('category_id')
        self.sku = kwargs.get('sku')
        self.description = kwargs.get('description')

    def save(self):
        return self.__class__.ez2.insert(self.__dict__)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'cost_price': self.cost_price,
            'sale_price': self.sale_price,
            'product_type': self.product_type,
            'category_id': self.category_id,
            'sku': self.sku
        }

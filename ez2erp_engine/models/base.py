from uuid import uuid4


class Ez2DBManager:
    dynamo_client = None

    def __init__(self, model_class, table_name):
        self.model_class = model_class
        self.table = self.dynamo_client.Table(table_name)

    @classmethod
    def connect_db(cls, session):
        cls.dynamo_client = session.resource('dynamodb')

    def select(self, key):
        # print(key)
        response = self.table.get_item(Key=key)
        print(response)
        return response

    def insert(self, item):
        print(item)
        response = self.table.put_item(Item=item)
        return response

    def save(self):
        pass

    # def select(self, *field_names):
    #     pass

    # def bulk_insert(self, rows: list):
    #     pass

    # def update(self, new_data: dict):
    #     pass

    # def delete(self):
    #     pass


class MetaModel(type):
    manager_class = Ez2DBManager
    
    def __new__(cls, name, bases, attrs):
        # cls.manager_class(model_class=cls)
        print(attrs)
        return super().__new__(cls, name, bases, attrs)

    @property
    def ez2(cls):
        return cls._get_manager()

    def _get_manager(cls):
        return cls.manager_class(
            model_class=cls,
            table_name=cls.table_name
        )


class BaseModel(metaclass=MetaModel):
    table_name = None

    def __init__(self, **kwargs):
        if 'id' in kwargs:
            self.id = kwargs['id'] 
        else:
            self.id = str(uuid4())
        

    # @property
    # def query_table(self):
    #     return self.table
    

# class BaseModel:
#     def __init__(self, dynamo_client, table_name=None):
#         self.dynamo_client = dynamo_client
#         self.table = self.dynamo_client.Table(table_name)

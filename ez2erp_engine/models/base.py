from uuid import uuid4
from boto3.dynamodb.conditions import Key


_default_limit = 50

class Ez2DBManager:
    dynamo_client = None

    def __init__(self, model_class, table_name):
        self.model_class = model_class
        self.table = self.dynamo_client.Table(table_name)

    @classmethod
    def connect_db(cls, session):
        cls.dynamo_client = session.resource('dynamodb')

    def _query_with_pagination_gsi(
            self, index_name, limit=_default_limit, 
            key_condition=None, filter_exp=None,
            last_evaluated_key=None
        ):
        params = {
            "IndexName": index_name, # Name of the GSI
            "Limit": limit,
        }

        if key_condition:
            params['KeyConditionExpression'] = key_condition
        
        if filter_exp:
            params['FilterExpression'] = filter_exp 
        
        if last_evaluated_key:
            params["ExclusiveStartKey"] = last_evaluated_key

        response = self.table.query(**params)
        
        items = response.get("Items", [])
        last_key = response.get("LastEvaluatedKey", None)

        print("items", items)
        result = []
        for item in items:
            result.append(self.model_class(**item))

        return result, last_key

    def select(self,
            index_name,
            limit=_default_limit,
            key_condition=None, 
            filter_exp=None, 
            last_evaluated_key=None
        ):
        return self._query_with_pagination_gsi(
            index_name=index_name,
            limit=limit,
            key_condition=key_condition,
            filter_exp=filter_exp,
            last_evaluated_key=last_evaluated_key
        )


    def select_dev(self):
        # TODO
        pass
        # resp = client.query(
        #     TableName='UsersTabe',
        #     IndexName='MySecondaryIndexName',
        #     ExpressionAttributeValues={
        #         ':v1': {
        #             'S': 'some@email.com',
        #         },
        #     },
        #     KeyConditionExpression='emailField = :v1',
        #     )

    def select_by_index(self, index_name, key_condition):
        response = self.table.query(
            IndexName=index_name,
            KeyConditionExpression=key_condition
        )

        if len(response['Items']) == 0:
            return None
        result = self.model_class(**response['Items'][0]) 
        return result


    def insert(self, item):
        print(item)
        response = self.table.put_item(Item=item)
        return response

    def save(self):
        pass



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

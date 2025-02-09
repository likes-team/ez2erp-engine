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
            self, **kwargs
        ):
        index_name = kwargs.get('index_name')
        limit = kwargs.get('limit')
        key_condition = kwargs.get('key_condition')
        filter_exp = kwargs.get('filter_exp')
        last_evaluated_key = kwargs.get('last_evaluated_key')

        params = {
            'IndexName': index_name,
            "Limit": limit
        }
        # if index_name:
        #     params[''] = index_name
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
    
    def _scan_with_pagination(self, **kwargs):
        limit = kwargs.get('limit')
        params = {
            "Limit": limit,  # Number of items per scan request
        }

        last_evaluated_key = kwargs.get('last_evaluated_key')
        if last_evaluated_key:
            params["ExclusiveStartKey"] = last_evaluated_key

        response = self.table.scan(**params)
        
        items = response.get("Items", [])
        last_key = response.get("LastEvaluatedKey", None)
        print("items", items)
        print("last_key", last_key)
        result = []
        for item in items:
            result.append(self.model_class(**item))
        return result, last_key

    def select(self,
            index_name=None,
            limit=_default_limit,
            key_condition=None, 
            filter_exp=None, 
            last_evaluated_key=None
        ):

        if index_name is None:
            return self._scan_with_pagination(
                limit=limit,
                last_evaluated_key=last_evaluated_key
            )

        return self._query_with_pagination_gsi(
            index_name=index_name,
            limit=limit,
            key_condition=key_condition,
            filter_exp=filter_exp,
            last_evaluated_key=last_evaluated_key
        )

    def get(self, oid):
        response = self.table.get_item(Key={'id': oid})
        item = response['Item']
        result = self.model_class(**item)
        return result

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
    
    def db_save(self, db_id, item):
        if db_id:
            return self._update(db_id, item)
        return self._insert(item)

    def _insert(self, item):
        print(item)
        response = self.table.put_item(Item=item)
        return response

    def _update(self, id, item):
        update_exp, exp_attr_values = self._get_update_params(item)
        print(update_exp)
        print(exp_attr_values)
        response = self.table.update_item(
            Key={"id": id},
            UpdateExpression=update_exp,
            ExpressionAttributeValues=dict(exp_attr_values)
        )
        return response

    def _get_update_params(item):
        update_expression = ["set "]
        update_values = dict()

        for key, val in item.items():
            update_expression.append(f" {key} = :{key},")
            update_values[f":{key}"] = val

        return "".join(update_expression)[:-1], update_values

    def delete(self, id):
        self.table.delete_item(
            Key={
                'id': id
            }
        )
        return id


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

        self.in_db = kwargs.get('in_db', False)

    def save(self):
        db_id = None

        # Check if data is already existing in DB then just update it
        if self.in_db: db_id = self.id

        item = self.__dict__
        return self.__class__.ez2.db_save(db_id, item)


    # @property
    # def query_table(self):
    #     return self.table
    

# class BaseModel:
#     def __init__(self, dynamo_client, table_name=None):
#         self.dynamo_client = dynamo_client
#         self.table = self.dynamo_client.Table(table_name)

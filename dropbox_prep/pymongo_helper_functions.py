from io import StringIO
from pymongo import MongoClient, errors

db_uri = "mongodb://localhost:27017"
client = MongoClient(host=db_uri, serverSelectionTimeoutMS=1000)

class PymongoHelperFunctions:
    def insert(self, document, collection_name, db_name="test"):
        db = client[db_name]
        collection = db[collection_name]
        if isinstance(document, list):
            insertion = collection.insert_many(document)
        else:
            insertion = collection.insert_one(document)
        return insertion.inserted_id


    def find(self, query, collection_name, db_name="test"):
        db = client[db_name]
        collection = db[collection_name]
        queried_documents = collection.find(query)
        queried_list = []
        for mongo_doc in queried_documents:
            queried_list.append(mongo_doc)
        return queried_list


    def remove_one_document(self, query, collection_name, db_name="test"):
        db = client[db_name]
        collection = db[collection_name]
        return collection.delete_one(query).deleted_count


    def replace_one_document(self, query, replacement, collection_name, db_name="test"):
        db = client[db_name]
        collection = db[collection_name]
        collection.replace_one(query, replacement)


    def drop_collection(self, collection_name, db_name="test"):
        db = client[db_name]
        collection_to_drop = db[collection_name]
        collection_to_drop.drop()


    def get_all_collections(self, db_name="test"):
        db = client[db_name]
        return db.list_collection_names()


    def drop_all_collections(self, db_name="test"):
        db = client[db_name]
        collection_list = self.get_all_collections(db_name=db_name)
        for collection in collection_list:
            col = db[collection]
            col.drop()


    def query_all(self, collection_name, db_name="test"):
        db = client[db_name]
        collection = db[collection_name]
        collection_list = []
        for item in collection.find():
            collection_list.append(item)
        return collection_list



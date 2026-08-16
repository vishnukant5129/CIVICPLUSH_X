import asyncio
from pymongo import AsyncMongoClient

async def test():
    client = AsyncMongoClient("mongodb://localhost:27017")
    db = client["testdb"]
    
    # Check what aggregate returns
    res = db["test"].aggregate([{"$match": {}}])
    print(type(res))
    
    res_find = db["test"].find({})
    print(type(res_find))

asyncio.run(test())

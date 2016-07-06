from pymongo import MongoClient
import pymongo
from bson.objectid import ObjectId
import datetime

# 创建客户端
client = MongoClient("localhost", 27017)

# 连接test数据库
db = client.test

post = {"author": "Hoda", "text": "hello mongodb!", "date": datetime.datetime.utcnow()}

# 获取集合
posts = db.posts

# # 向集合中插入值
# post_id = posts.insert_one(post).inserted_id
#
# print(post_id)

# print(db.collection_names(include_system_collections=False))

## 从集合中查询一个文档
# one = posts.find_one()
# print(one)
#
# one = posts.find_one({"author":"Hoda"})
# print(one)
#
# # _id类型是ObjectId 不同于字符串
# post_id ="577cc15d88ace31adc7c6e64"
# one = posts.find_one({"_id":ObjectId(post_id)})
# print(one)

# # 插入数据的字段可以不同，模式自由，避免空字段开销（Schema Free）
# new_posts = [{"author": "Mike",
#               "text": "Another post!",
#               "tags": ["bulk", "insert"],
#               "date": datetime.datetime(2009, 11, 12, 11, 14)},
#              {"author": "Eliot",
#               "title": "MongoDB is fun",
#               "text": "and pretty easy too!",
#               "date": datetime.datetime(2009, 11, 10, 10, 45)}]
#
# # 批量添加
# result = posts.insert_many(new_posts)
# print(result.inserted_ids)

# # 批量查询
# for post in posts.find():
#     print(post)
#
# for post in posts.find({"author":"Mike"}):
#     print(post)

# # 统计数量
# count = posts.count()
# print(count)
# count = posts.count({"author":"Mike"})
# print(count)

# 排序
# d = datetime.datetime(2009, 11, 12, 12)
# for post in posts.find({"date":{"$lt":d}}).sort("author"):
#     print(post)

# 索引
# profiles = db.profiles
# 添加升序、唯一索引
# result = profiles.create_index([("user_id", pymongo.ASCENDING)], unique=True)
# print(list(profiles.index_information()))

# user_profiles = [
#     {'user_id': 211, 'name': 'Luke'},
#     {'user_id': 212, 'name': 'Ziltoid'}]
# result = profiles.insert_many(user_profiles)
# print(result)

# new_profile = {'user_id': 213, 'name': 'Drew'}
# duplicate_profile = {'user_id': 212, 'name': 'Tommy'}
# result = profiles.insert_one(new_profile)
# result = db.profiles.insert_one(duplicate_profile)

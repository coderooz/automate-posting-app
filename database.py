from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['social_media_db']

def store_post_data(post_id, platform, data):
    db.posts.insert_one({
        'post_id': post_id,
        'platform': platform,
        'data': data
    })

import redis

def cache_clean():
    conn = redis.StrictRedis(host='localhost',port=6379,db=2)
    print('----------clean')
    for key in conn.keys():
        if 'bookstore-index' in key.decode('utf8'):
            conn.delete(key)
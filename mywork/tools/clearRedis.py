import redis
pool = redis.ConnectionPool(host='192.168.1.48', port=6379, decode_responses=True)
conn = redis.Redis(connection_pool=pool)
list_keys = conn.keys("DETAIL_FAULTS_CONVERT_*")

for key in list_keys:
    conn.delete(key)
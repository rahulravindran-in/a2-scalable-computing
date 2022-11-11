from aiohttp import web
import redis
from cassandra.cluster import Cluster
from CacheDict import CacheDict

config = {
    "redis": {
        "port": 6379,
        "host": "redis",
        "db": 0
    },
    "cassandra": {
        "host": "0.0.0.0",
        "port": 9042
    },
    "cache_size": 10000
}

app = web.Application()


local_cache = CacheDict(cache_len=config["cache_size"])
redis_session = redis.Redis(host=config["redis"]["host"], port=config["redis"]["port"], db=config["redis"]["db"]) # Use 0 or 1
cassandra_cluster = Cluster([config["cassandra"]["host"]], port=config["cassandra"]["port"])
cassandra_session = cassandra_cluster.connect('kvp', wait_for_all_pools=False)

def short_to_long(short: str):
    ans = ""

    # If in local cache
    if short in local_cache:
        ans = local_cache[short]
    else:
        cache_val = redis_session.get(short)
        # If in redis cache
        if cache_val:
            ans = cache_val
        else:
            # Finally, try Cassandra
            ans = cassandra_get(short)

    if ans:
        return web.Response(text=ans, content_type='text/html', status=307)
    else:
        return web.Response(text="", content_type='text/html', status=404)


def long_to_short(short: str, long: str):
    local_cache[short] = long
    redis_session.set(short, long)
    cassandra_put(short, long)
    return web.Response(text="Long to Short", content_type='text/html')


async def router(request):
    if not("short" in request.query and "long" in request.query):
        return web.Response(text="Bad Request Type", content_type='text/html', status=400)

    if request.method == 'GET':
        return short_to_long(short=request.query["short"])

    if request.method == 'PUT':
        return long_to_short(short=request.query["short"], long=request.query["long"])

    return web.Response(text="Bad Request Type", content_type='text/html', status=400)

app.router.add_get('/{tail:.*}', router)


def cassandra_get(short):
    rows = cassandra_session.execute(
        "SELECT long FROM kvp WHERE short = '{short}';"
            .format(short=short)
    )
    long_maybe = [row[0] for row in rows]
    return long_maybe[0] if len(long_maybe) >= 1 else None


def cassandra_put(short, long):
    cassandra_session.execute(
        "INSERT INTO kvp (long, short) VALUES ('{long}', '{short}')"
            .format(long=long, short=short)
    )


if __name__ == '__main__':
    web.run_app(app, port=8080)
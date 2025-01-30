import os
from redis.asyncio import Redis
from redis.backoff import ExponentialBackoff, NoBackoff
from redis.exceptions import ConnectionError, TimeoutError
from redis.retry import Retry


def initialize_redis_bytes():
    return Redis(
        host=os.environ.get("REDISHOST", "localhost"),
        port=int(os.environ.get("REDISPORT", 6379)),
        username=os.environ.get("REDISUSER", None),
        password=os.environ.get("REDISPASSWORD", None),
        db=0,
        ssl=bool(os.environ.get("REDISSSL", False)),
        ssl_cert_reqs="none",
    )


def initialize_redis(retries: int = 1):
    backoff = ExponentialBackoff() if retries > 1 else NoBackoff()
    retry = Retry(backoff, retries)
    return Redis(  # type: ignore
        host=os.environ.get("REDISHOST", "localhost"),
        port=int(os.environ.get("REDISPORT", 6379)),
        username=os.environ.get("REDISUSER", None),
        password=os.environ.get("REDISPASSWORD", None),
        decode_responses=True,
        retry=retry, # type: ignore
        ssl=bool(os.environ.get("REDISSSL", False)),
        ssl_cert_reqs="none",
        retry_on_error=[ConnectionError, TimeoutError],
        health_check_interval=30,
    )


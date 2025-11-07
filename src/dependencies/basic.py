import os
import ssl
from typing import Generator, Union

from redis import RedisCluster, StrictRedis
from sqlalchemy.orm import Session

from src.database.database import SessionLocal


def get_redis_client(db: int = 0) -> Generator[Union[RedisCluster, StrictRedis], None, None]:
    """
    FastAPI dependency for Redis client that supports both Redis Cluster (AWS ElastiCache) and standalone Redis.
    
    Usage:
        @app.get("/endpoint")
        def my_endpoint(redis: Redis = Depends(get_redis_client)):
            redis.set("key", "value")
    
    Args:
        db: Database number (only used for standalone Redis, clusters don't support db selection)
    
    Yields:
        RedisCluster or StrictRedis instance
    """
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    if os.getenv('REDIS_CLUSTER', 'false').lower() == 'true':
        # Redis Cluster doesn't support database selection - all data goes to db=0
        # This fallback ensures consistent behavior across cluster and standalone modes
        r = RedisCluster(
            host=os.getenv('REDIS_HOST', 'redis'),
            port=int(os.getenv('REDIS_PORT', '6379')),
            decode_responses=True,
            ssl=True,
            ssl_context=ssl_context,
            socket_connect_timeout=5,
            socket_timeout=5,
            skip_full_coverage_check=True
        )
    else:
        # Standalone Redis with database selection support
        r = StrictRedis(
            host=os.getenv('REDIS_HOST', 'redis'),
            port=int(os.getenv('REDIS_PORT', '6379')),
            db=db,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
    
    try:
        yield r
    finally:
        r.close()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database session.
    
    Usage:
        @app.get("/endpoint")
        def my_endpoint(db: Session = Depends(get_db)):
            db.query(User).all()
    
    Yields:
        SQLAlchemy Session instance
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

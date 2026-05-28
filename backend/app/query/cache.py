import hashlib, json, time, os, logging
logger = logging.getLogger(__name__)
_mem: dict = {}
TTL = 30
_redis = None

# Try connecting Redis if REDIS_URL env var exists, silently skip if not
try:
    url = os.getenv("REDIS_URL")
    if url:
        import redis
        _redis = redis.from_url(url, decode_responses=True, socket_timeout=0.5)
        _redis.ping()
except Exception:
    _redis = None

def _key(role: str, query: str) -> str:
    raw = f"{role}:{' '.join(query.lower().split())}"
    return hashlib.sha256(raw.encode()).hexdigest()[:24]

def get(role: str, query: str):
    k = _key(role, query)
    if _redis:
        try:
            v = _redis.get(f"naa:{k}")
            if v: return json.loads(v), True
        except Exception: pass
    if k in _mem:
        val, exp = _mem[k]
        if time.time() < exp: return val, True
        del _mem[k]
    return None, False

def set(role: str, query: str, value) -> None:
    k = _key(role, query)
    _mem[k] = (value, time.time() + TTL)
    if _redis:
        try: _redis.setex(f"naa:{k}", TTL, json.dumps(value, default=str))
        except Exception: pass

class GlobalQueryCache:
    def get(self, role: str, query: str):
        val, hit = get(role, query)
        return val if hit else None
        
    def set(self, role: str, query: str, value) -> None:
        set(role, query, value)

global_query_cache = GlobalQueryCache()


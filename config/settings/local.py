from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Console Backend for emails in development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Override cache to use local Redis in dev
# (fallback to LocMem if Redis is not running)
try:
    import redis
    r = redis.Redis(host='localhost', port=6379, db=1)
    r.ping()
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': 'redis://localhost:6379/1',
            'KEY_PREFIX': 'eduflow_dev',
            'TIMEOUT': 300,
        }
    }
except Exception:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }

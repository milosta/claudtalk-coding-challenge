from .base import *  # noqa: F401,F403
from .base import env

DEBUG = True
ALLOWED_HOSTS = env("ALLOWED_HOSTS", default=["*"])
INTERNAL_IPS = ["127.0.0.1"]

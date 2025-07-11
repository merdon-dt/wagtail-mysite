from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-4mmd_a^14l1x&p2+ijqn!rhf)e7la=uc0lonmdgur6w@ljv)wb"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

INSTALLED_APPS = INSTALLED_APPS + [
    "debug_toolbar",
]

MIDDLEWARE = MIDDLEWARE + [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

INTERNAL_IPS = [
    "127.0.0.1",
]

try:
    from .local import *
except ImportError:
    pass

CACHES = {
    "default" : {
        "BACKEND" : "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION" : "D:\Merdon\WorkSpace\Wagtail\mysite\cache",
    }
}
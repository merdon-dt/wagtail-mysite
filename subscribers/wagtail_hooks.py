from wagtail import hooks
from .admin import SubscriberViewSet

@hooks.register("register_admin_viewset")
def register_subscriber_viewset():
    return SubscriberViewSet()

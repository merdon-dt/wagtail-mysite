from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.admin.ui.tables import Column
from .models import Subscriber

class SubscriberViewSet(ModelViewSet):
    model = Subscriber
    icon = "login"
    add_to_admin_menu = True
    menu_label = "Subscribers"
    menu_order = 200

    # ✅ REQUIRED for Wagtail 5+ ViewSets
    form_fields = ["email", "full_name"]

    list_display = [
        Column("email", label="Email"),
        Column("full_name", label="Full Name"),
    ]

    search_fields = ["email", "full_name"]

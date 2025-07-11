from django.db import models

class Subscriber(models.Model):  # Renamed for clarity and consistency
    email = models.EmailField()
    full_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.full_name or self.email  # Fallback to email if name is blank

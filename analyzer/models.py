from django.db import models

class TrustedReference(models.Model):
    label = models.CharField(max_length=100)
    filename = models.CharField(max_length=255)
    sha256 = models.CharField(max_length=64, db_index=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    record_type = models.CharField(max_length=80, default='Django database (not blockchain)')

    def __str__(self):
        return f'{self.label} ({self.sha256[:12]}...)'

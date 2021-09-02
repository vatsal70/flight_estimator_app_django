from django.db import models

# Create your models here.
import uuid

class FlightDetails(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    Journey_month = models.CharField(max_length=100)
    Journey_day = models.CharField(max_length=100)
    Journey_year = models.CharField(max_length=100)
    Dep_hour = models.CharField(max_length=100)
    Dep_min = models.CharField(max_length=100)
    Arr_hour = models.CharField(max_length=100)
    Arr_min = models.CharField(max_length=100)
    Total_Stops = models.CharField(max_length=100)
    Duration_hours = models.CharField(max_length=100)
    Duration_mins = models.CharField(max_length=100)
    airline = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    price = models.CharField(max_length=100,)
    
    def __str__(self):
        return str(self.id)
    
    class Meta:
        verbose_name_plural = "Flight Details"
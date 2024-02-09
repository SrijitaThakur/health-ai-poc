from djongo import models


class HeartRates(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    startDate = models.DateTimeField()
    endDate = models.DateTimeField()
    value = models.IntegerField()


class Sleep(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    startDate = models.DateTimeField()
    endDate = models.DateTimeField()
    # Example values: asleep, awake, deep sleep, etc.
    value = models.CharField(max_length=20)


class User(models.Model):
    class Meta:
        db_table = "Users"  # Specify the desired collection name
    _id = models.ObjectIdField(primary_key=True)
    email = models.EmailField()
    age = models.CharField(max_length=10)
    sex = models.CharField(max_length=10)
    height = models.CharField(max_length=10)
    weight = models.CharField(max_length=10)
    bloodSugar = models.FloatField()
    dietaryFatTotal = models.FloatField()
    dietarySugar = models.FloatField()
    dietaryWater = models.FloatField()
    dietaryProtein = models.FloatField()
    dietaryFiber = models.FloatField()
    bloodPressureSystolic = models.FloatField()
    bloodPressureDiastolic = models.FloatField()
    heartRates = models.ArrayField(model_container=HeartRates)
    sleep = models.ArrayField(model_container=Sleep)
    steps = models.IntegerField()
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

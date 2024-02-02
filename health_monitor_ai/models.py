from djongo import models


class HeartRates(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    date = models.DateField()
    value = models.IntegerField()


class Sleep(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    from_date = models.DateField()
    to_date = models.DateField()
    # Example values: asleep, awake, deep sleep, etc.
    sleep_value = models.CharField(max_length=20)


class Steps(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    date = models.DateField()
    steps = models.IntegerField()


class User(models.Model):
    class Meta:
        db_table = "Users"  # Specify the desired collection name
    _id = models.ObjectIdField(primary_key=True)
    email = models.EmailField()
    age = models.CharField(max_length=10)
    sex = models.CharField(max_length=10)
    height = models.CharField(max_length=10)
    weight = models.FloatField()
    targetWeight = models.FloatField()
    purpose = models.CharField(max_length=100)
    heartRates = models.ArrayField(model_container=HeartRates)
    sleep = models.ArrayField(model_container=Sleep)
    steps = models.ArrayField(model_container=Steps)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

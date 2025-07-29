from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class PrayerActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_active = models.DateTimeField(auto_now=True)
    region = models.CharField(max_length=100)
    lat = models.FloatField(null=True)
    lng = models.FloatField(null=True)

class PrayerSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mystery = models.CharField(max_length=50)
    completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(default=timezone.now)

class Prayer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    text = models.TextField()

    def __str__(self):
        return self.name


class MysterySet(models.Model):
    name = models.CharField(max_length=50, unique=True)  # Joyful, Sorrowful...
    days = models.CharField(max_length=100)  # e.g. "Monday, Saturday"

    def __str__(self):
        return self.name


class Mystery(models.Model):
    set = models.ForeignKey(MysterySet, on_delete=models.CASCADE, related_name='mysteries')
    title = models.CharField(max_length=100)
    scripture_reference = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.set.name} - {self.title}"


class DecadeStep(models.Model):
    mystery = models.ForeignKey(Mystery, on_delete=models.CASCADE, related_name='steps')
    order = models.PositiveIntegerField()
    prayer = models.ForeignKey(Prayer, on_delete=models.PROTECT)
    repeat = models.PositiveIntegerField(default=1)  # 1 for Glory Be, 10 for Hail Mary, etc.

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.mystery.title} - Step {self.order}: {self.prayer.name} x{self.repeat}"
class PrayerSequence(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class PrayerSequenceStep(models.Model):
    sequence = models.ForeignKey(PrayerSequence, on_delete=models.CASCADE, related_name='steps')
    order = models.PositiveIntegerField()
    prayer = models.ForeignKey(Prayer, on_delete=models.PROTECT)
    repeat = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.sequence.name} - Step {self.order}: {self.prayer.name} x{self.repeat}"

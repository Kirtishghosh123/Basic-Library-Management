from django.db import models
from django.db.models import CASCADE
from django.contrib.auth.models import User

# Create your models here.

class Author(models.Model):
    objects = None
    name = models.CharField(max_length=120)
    birthdate = models.DateField()
    nationality = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Book(models.Model):
    DoesNotExist = None
    objects = None
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=CASCADE)
    genre = models.CharField(max_length=125)
    publication_date = models.DateField()
    available_copies = models.IntegerField()

    def __str__(self):
        return self.title

class Borrow(models.Model):
    objects = None
    user = models.ForeignKey(User, on_delete=CASCADE)
    book = models.ForeignKey(Book, on_delete=CASCADE)
    borrow_date = models.DateField(blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)
    is_returned = models.BooleanField()
    copies_requested = models.PositiveIntegerField(default=1, null=True, blank=True)
    copies_returned = models.PositiveIntegerField(default=0,blank=True, null=True)

    def __str__(self):
        return str(self.user.username).upper() + " logs"

    class Meta:
        verbose_name = 'Borrow and Return'
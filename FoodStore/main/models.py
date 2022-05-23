from django.contrib.postgres.fields import ArrayField
from django.db import models

# Create your models here.
from django.forms import forms


class Address(models.Model):
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    house = models.CharField(max_length=255)


class User(models.Model):
    fullName = models.CharField(max_length=30)
    email = models.CharField(max_length=40)
    phoneNumber = models.CharField(max_length=15)
    gender = models.CharField(max_length=10)
    password = models.CharField(max_length=255)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    balance = models.IntegerField(default=15000)

    def __str__(self):
        return {
            'fullName': self.fullName,
            'email': self.email,
            'phoneNumber': self.phoneNumber,
            'gender': self.gender,
            'password': self.password,
            'address': self.address,
        }


class Product(models.Model):
    picture = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    category = models.CharField(max_length=30)
    price = models.IntegerField()


class Dish(models.Model):
    picture = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True)
    ingredients = ArrayField(models.IntegerField())
    cookingSteps = ArrayField(
        ArrayField(
            models.CharField(max_length=500),  # first step, second image
            size=2
        )
    )


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.IntegerField()


class Bill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=1024)
    totalPrice = models.IntegerField()


class CartForm(forms.Form):
    class Meta:
        model = Cart
        fields = '__all__'


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    text = models.CharField(max_length=1024)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ingredient_id = models.IntegerField(null=True)
    dish_id = models.IntegerField(null=True)
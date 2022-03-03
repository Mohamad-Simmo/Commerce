from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=24)

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bid")
    amount = models.DecimalField(decimal_places=2, max_digits=11, null=True)

    def __str__(self):
        return f"{self.user}: {self.amount}"
    
class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    image = models.TextField(blank=True, null=True)
    starting_bid = models.DecimalField(decimal_places=2, max_digits=11)
    highest_bid = models.ForeignKey(Bid,blank=True, null=True, on_delete=models.SET_NULL, related_name="listing_highest_bid")
    is_active = models.BooleanField()
    winner = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="winner")
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE, related_name="category")
    bids = models.ManyToManyField(Bid, blank=True, related_name="listing_bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_listing")

class Comment(models.Model):
    comment = models.TextField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_comment")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comment")

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="user_watchlist")
    listing = models.ForeignKey(Listing, on_delete=models.PROTECT, related_name="listing_watchlist")
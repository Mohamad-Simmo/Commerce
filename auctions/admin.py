from django.contrib import admin

from .models import Category, Listing, Bid, Comment, Watchlist


class ListAdmin(admin.ModelAdmin):
    filter_horizontal = ("bids",)

# Register your models here.
admin.site.register(Category)
admin.site.register(Listing, ListAdmin)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Watchlist)
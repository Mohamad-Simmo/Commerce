from logging import exception
from unicodedata import digit
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listing, Bid, Comment, Watchlist

def index(request):
    # Show all active listings
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(is_active=True)
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    # Logout user
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create_listing(request):
    if request.method == 'POST':
        title = request.POST["title"]
        description = request.POST["description"]
        image = request.POST["image_url"]
        starting_bid = request.POST["starting_bid"]
        is_active = True
        category = request.POST["category"]

        if category:
            try:
                #  Get category if it exists
                category = category.capitalize()
                category = Category.objects.get(name=category)
            except:
                # Create new category
                category = Category.objects.create(name=category.capitalize())
        else:
            # User did not input a category
            category = None


        try:
            # Create new listing object
            Listing.objects.create (
                title=title,
                description=description,
                image=image, 
                starting_bid=starting_bid,
                is_active=is_active, 
                category=category,
                user=request.user
            )

        except:
            # Invalid inputs
            return render(request, "auctions/create_listing.html", {
                "categories": Category.objects.all(),
                "message": "Invalid input"
            })

        # Listing created successfully
        return HttpResponseRedirect(reverse("index"))


    # request.method == 'GET'
    return render(request, "auctions/create_listing.html", {
        "categories": Category.objects.all()
    })


def listing_view(request, listing_id):
    current_listing = Listing.objects.get(id=listing_id)
    bids = current_listing.bids.all()
    comments = Comment.objects.filter(listing=current_listing)

    # Check if listing is in watchlist
    try:
        watchlist = Watchlist.objects.get(listing=current_listing)
    except Watchlist.DoesNotExist:
        watchlist = None


    if request.method == 'POST':
        if 'submit_bid' in request.POST:

            # Check bid
            try:
                new_bid_amount = float(request.POST["bid"])
            except ValueError:
                return render(request, "auctions/listing.html", {
                    "listing": current_listing,
                    "bids": bids,
                    "message": "Invalid bid amount"
                })

            # New bid > start price
            if new_bid_amount >= float(current_listing.starting_bid):

                # New bid > highest bid
                if current_listing.highest_bid is None or float(current_listing.highest_bid.amount) < new_bid_amount:
                    
                    # Add new bid to listing
                    new_bid_object = Bid.objects.create(user=request.user, amount=new_bid_amount)
                    current_listing.highest_bid = new_bid_object
                    current_listing.bids.add(new_bid_object)
                    current_listing.save()

                    return HttpResponseRedirect(reverse('listing', args=(current_listing.id,)))

                # New bid < highest bid  
                else:
                    return render(request, "auctions/listing.html", {
                        "listing": current_listing,
                        "bids": bids,
                        "message": "Your bid should be equal to or greater than the starting price"
                    })

            # New bid < start price
            else:
                return render(request, "auctions/listing.html", {
                    "listing": current_listing,
                    "bids": bids,
                    "message": "Your bid should be greater than the highest bid"
                })

        elif 'submit_watchlist' in request.POST:

            # Add listing to watchlist
            Watchlist.objects.create(user=request.user, listing=current_listing)

            return HttpResponseRedirect(reverse('listing', args=(current_listing.id,)))

        elif 'submit_remove_watchlist' in request.POST:

            # Remove listing from watchlist
            Watchlist.objects.get(listing=current_listing).delete()

            return HttpResponseRedirect(reverse('listing', args=(current_listing.id,)))

        elif 'submit_close_listing' in request.POST:

            # Close listing and pick the winner
            current_listing.is_active = False
            if not current_listing.highest_bid is None:
                current_listing.winner = current_listing.highest_bid.user
            current_listing.save()

            return HttpResponseRedirect(reverse('listing', args=(current_listing.id,)))

        elif 'submit_comment' in request.POST:
            comment = request.POST["comment"]

            if len(comment.strip()) > 0:
                # Add new comment to listing
                Comment.objects.create(user=request.user, listing=current_listing, comment=comment)

            return HttpResponseRedirect(reverse('listing', args=(current_listing.id,)))


    # request.method == 'Get'
    return render(request, "auctions/listing.html", {
        "listing": current_listing,
        "bids": bids,
        "watchlist": watchlist,
        "comments": comments
    })


def watchlist(request):
    watchlist = Watchlist.objects.filter(user=request.user)
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist
    })


def categories_view(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def category(request, category_name):
    listings = Listing.objects.filter(category=Category.objects.get(name=category_name))
    return render(request, "auctions/category.html", {
        "listings": listings
    })
import datetime
import json
from pprint import pprint
from random import shuffle

from django.core.files.storage import FileSystemStorage
from django.http import response, JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.db.models import Q
# Create your views here.
from main.models import Address, User, Dish, Product, Cart, CartForm, Comment, History


def index(req):
    # checking if we have authorized user
    if not req.session.get('user'):
        # if we don't then we redirect user to auth page
        return redirect('/authorize')
    # getting authorized user id
    userId = req.session.get('user')
    # getting list of all dishes
    dish = Dish.objects.first()
    dishes = Dish.objects.all().exclude(pk=dish.id)
    # we need to get first and exclude it from list for carousel elements in main page
    nums = []  # amount of dishes
    for i in range(1, len(dishes) + 1):
        nums.append(i)

    # getting user model by user id
    user = User.objects.get(id=int(userId))

    # amount of elements in user's cart
    items = Cart.objects.filter(user_id=req.session['user'])
    sum = len(items)

    history = History.objects.filter(user_id=req.session['user'])
    prevProdIds = []

    for h in history:
        prevProdIds.append(h.ingredient_id)

    recCategory = []

    for pId in prevProdIds:
        try:
            prod = Product.objects.get(pk=pId)
            if prod.category not in recCategory:
                recCategory.append(prod.category)
        except:
            pass

    recs = Product.objects.filter(Q(category__in=recCategory))
    recs = (list(recs))
    shuffle(recs)
    recs = recs[:12]
    # here we are sending data to our template (index.html)
    return render(req, 'index.html', {
        'user': user,
        'first_dish': dish,
        'nums': nums,
        'dishes': dishes,
        'products': Product.objects.all(),
        'cartItemsAmount': sum,
        'cartItems': items,
        'recommendations': recs,
    })


def dishPage(req, dish_id):
    # getting list if all dishes
    dish = Dish.objects.get(pk=dish_id)
    # getting ingredients for dish
    ingredients = Product.objects.filter(pk__in=dish.ingredients)
    # getting steps to cook
    steps = []
    if not History.objects.filter(user_id=req.session['user']).filter(dish_id=dish_id):
        history = History(user_id=req.session['user'], dish_id=dish_id)
        history.save()
    # reformatting steps in a way that will be easier to use
    for i in range(len(dish.cookingSteps)):
        steps.append({
            'number': i + 1,
            'image': dish.cookingSteps[i][0],
            'text': dish.cookingSteps[i][1],
        })
    # getting comments list
    comments = Comment.objects \
        .filter(dish_id=dish.id) \
        .order_by('created_at') \
        .reverse()  # ordering by created date and reversing it so that first we will see fresh comments =D
    # getting cart items for user
    items = Cart.objects.filter(user_id=req.session['user'])
    # getting cart items amount user
    sum = len(items)
    # sending data
    return render(req, 'dish.html', {
        'dish': dish,
        'ingredients': ingredients,
        'steps': steps,
        'comments': comments,
        'cartItemsAmount': sum
    })


def authorize(req):
    # method for sending authorize.html
    return render(req, 'authorize.html')


def product(req, product_id):
    # method for showing detailed information about product
    currProduct = Product.objects.get(pk=product_id)
    # getting product by product id
    if not History.objects.filter(user_id=req.session['user']).filter(ingredient_id=product_id):
        history = History(user_id=req.session['user'], ingredient_id=product_id)
        history.save()
    items = Cart.objects.filter(user_id=req.session['user'])
    # getting cart items amount user
    sum = len(items)
    return render(req, 'product.html', {
        'cartItemsAmount': sum,
        'product': currProduct
    })


def login(req):
    if req.method == 'POST':
        username = req.POST['email']
        password = req.POST['pass']

        errors = []
        try:
            user = User.objects.get(email=username, password=password)
            if user is None:
                errors.append('Invalid login or password')
            # error handling
            req.session['user'] = user.id
            # setting user id to session(that how our authorization is realized with custom model)
            return redirect('/', req)

        except User.DoesNotExist:
            errors.append('Invalid login or password')
        # in case if we did not find user we send that something is wrong
        if len(errors):
            return render(req, 'authorize.html', {
                'errors': errors
            })
        # errors are gonna be shown in the top of authorization like notification
        return render(req, 'authorize.html')


def logout(req):
    # deleting user from session
    del req.session['user']

    return redirect('/authorize')


def register(req):
    if req.method == 'POST':
        # address
        country = req.POST["country"]
        city = req.POST['city']
        street = req.POST['street']
        house = req.POST['house']

        address = Address(
            country=country,
            city=city,
            street=street,
            house=house
        )
        address.save()

        # user
        email = req.POST['email']
        phone = req.POST['phone']
        password = req.POST['pass']
        password2 = req.POST['pass2']

        errors = []

        duplicateUser = User.objects.filter(email=email)
        duplicateNumber = User.objects.filter(phoneNumber=phone)

        # error handling
        if len(duplicateUser):
            errors.append('Email must be unique')

        # error handling
        if len(duplicateNumber):
            errors.append('Number must be unique')

        # error handling
        if password != password2:
            errors.append('Passwords does not match')

        # error handling
        if len(errors):
            return render(req, 'authorize.html', {
                'errors': errors
            })

        name = req.POST['name']
        gender = req.POST['gender']
        new_user = User(
            fullName=name,
            email=email,
            phoneNumber=phone,
            gender=gender,
            password=password,
            address_id=address.id
        )
        new_user.save()
        # creating new user
        req.session['user'] = new_user.id

        return redirect('/', req)


def cart(req):
    items = Cart.objects.filter(user_id=req.session['user'])
    sum = 0
    count = len(items)
    if len(items):
        # getting sum to show it in the bottom
        for item in items:
            sum += item.amount * item.product.price
        # sending cart items for user
        return render(req, 'cart.html', {
            'items': items,
            'sum': sum,
            'cartItemsAmount': count,
        })
    # in case if our cart is empty we send another template
    return render(req, 'emptyCart.html')


def addProduct(req):
    items = Cart.objects.filter(user_id=req.session['user'])
    # amount of items in cart
    sum = len(items)
    # check if method is post in other case we return template
    if req.method == 'POST':
        picture = req.FILES['picture']
        # we used FileSystemStorage to save files which will be uploaded
        fs = FileSystemStorage()
        filename = fs.save(picture.name, picture)  # getting fileName
        uploaded_file_url = fs.url(filename)  # getting path to file

        name = req.POST['name']
        description = req.POST['description']
        category = req.POST['category']
        price = req.POST['price']

        newProduct = Product(name=name,
                             description=description,
                             category=category,
                             price=price,
                             picture=uploaded_file_url)  # here we save path to file(image)
        newProduct.save()

        return render(req, 'addProduct.html', {
            'cartItemsAmount': sum
        })
    return render(req, 'addProduct.html')


def addToCart(req, product_id):
    userCart = Cart(user_id=req.session['user'], product_id=product_id, amount=1)
    userCart.save()
    next = req.GET.get('next', '/')
    # redirecting back after adding item to cart
    return HttpResponseRedirect(next)


def removeFromCart(req, cart_id):
    userCart = Cart.objects.get(pk=cart_id)
    userCart.delete()
    # redirecting to cart
    return redirect('cart')


def payment(req):
    items = Cart.objects.filter(user_id=req.session['user'])
    sum = 0
    user = User.objects.get(pk=int(req.session['user']))
    if len(items):
        for item in items:
            sum += item.amount * item.product.price
        return render(req, 'payment.html', {
            'user': user,
            'items': items,
            'sum': sum
        })
    return redirect('cart')


def proceed(req, price):
    user = User.objects.get(pk=int(req.session['user']))
    user.balance -= price
    if user.balance < price:
        return render(req, 'notEnough.html')
    user.save()
    items = Cart.objects.filter(user_id=req.session['user'])
    items.delete()
    return redirect('index')


def updateCartProductAmount(req, cart_id, amount):
    pprint(cart_id)
    pprint(amount)
    cartItem = Cart.objects.get(pk=int(cart_id))
    cartItem.amount = int(amount)
    cartItem.save()
    return HttpResponse(status=200)


def addDish(req):
    items = Cart.objects.filter(user_id=req.session['user'])
    sum = len(items)
    if req.method == 'POST':
        picture = req.FILES['picture']
        fs = FileSystemStorage()
        filename = fs.save(picture.name, picture)
        uploaded_file_url = fs.url(filename)

        name = req.POST['name']
        ingredients = req.POST.getlist('ingredient_ids[]')

        dish = Dish(picture=uploaded_file_url, name=name, ingredients=ingredients, cookingSteps=[])
        dish.save()
        return render(req, 'addDish.html', {
            'cartItemsAmount': sum
        })
    return render(req, 'addDish.html', {
        'ingredients': Product.objects.all(),
        'cartItemsAmount': sum

    })


def addStep(req):
    if req.method == 'POST':
        picture = req.FILES['picture']
        fs = FileSystemStorage()
        filename = fs.save(picture.name, picture)
        uploaded_file_url = fs.url(filename)

        dish_id = req.POST['dish_id']
        text = req.POST['text']

        dish = Dish.objects.get(pk=dish_id)
        if dish.cookingSteps is None:
            dish.cookingSteps = []
        dish.cookingSteps.append([uploaded_file_url, text])
        dish.save()

    items = Cart.objects.filter(user_id=req.session['user'])
    sum = len(items)
    return render(req, 'addStep.html', {
        "dishes": Dish.objects.all(),
        'cartItemsAmount': sum
    })


def addComment(req):
    if req.method == 'POST':
        user_id = req.session['user']
        text = req.POST['text']
        dish_id = req.POST['dish_id']
        new_comment = Comment(user_id=user_id, text=text, dish_id=dish_id)
        new_comment.save()

        return redirect(f'dish/{dish_id}')


def about_us(req):
    return render(req, 'about_us.html')


def searchProduct(req):
    text = req.GET['text']
    if text == 'all':
        items = Product.objects.all()
    else:
        if text.isdigit():
            items = Product.objects.filter(price=text)
        else:
            items = Product.objects.filter(
                Q(name__icontains=text) |
                Q(description__icontains=text) |
                Q(category__icontains=text)
            )
    prods = Cart.objects.filter(user_id=req.session['user'])
    sum = len(prods)
    return render(req, 'search.html', {
        'search_text': text,
        'items': items,
        'cartItemsAmount': sum
    })

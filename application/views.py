from django.shortcuts import render, redirect
from .models import *
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from datetime import datetime
from django.db.models import Sum

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import hashlib as hl

from random import randint

# main page function

def index(request):
    context = {}
    if request.user.is_authenticated:
        context['cart_items'] = get_cart_items(request)

    if len(products.objects.all())>0:
        context['all_products'] = products.objects.all()[0:3]

    return render(request, 'index.html', context)

def profile(request):
    if not request.user.is_authenticated:
        return redirect("index")

    context = {}


    context['cart_items'] = get_cart_items(request)



    if request.method == 'POST':
        card_number = request.POST['card_num']
        cvv_number = request.POST['cvv_num']
        exp_date = request.POST['exp_date']

        print(card_number)
        print(cvv_number)
        print(exp_date)

        if not credit_cards.objects.filter(person=request.user).exists():
            new_card = credit_cards(person=request.user, card_number=card_number, cvv_number=cvv_number, exp_date=exp_date)
            new_card.save()

    context['credit_status'] = credit_cards.objects.filter(person=request.user).exists()

    if context['credit_status']:
        context['credit_details'] = credit_cards.objects.get(person=request.user)

    context['isSeller'] = user_more_info.objects.filter(person=request.user).exists()

    if 'section' in request.GET:
        if request.GET['section']=='products':
            if context['isSeller'] and products.objects.filter(seller=request.user).exists():
                context['all_products'] = products.objects.filter(seller=request.user)
                print('all products sent')

        if request.GET['section'] == 'cart':
            if myCart.objects.filter(buyer=request.user).exists():
                context['all_cart_items'] = myCart.objects.filter(buyer=request.user)
                context['total_items'] = context['all_cart_items'].count()
                context['total_bill'] = context['all_cart_items'].aggregate(Sum('amount'))['amount__sum']

        if request.GET['section'] == 'placed_orders':
            if order.objects.filter(order_buyer=request.user).exists():
                context['all_orders'] = order.objects.filter(order_buyer=request.user)
                print(context['all_orders'])

        if request.GET['section'] == 'received_orders':
            if order.objects.filter(order_seller=request.user).exists():
                context['all_orders'] = order.objects.filter(order_seller=request.user)
                print(context['all_orders'])


    return render(request, 'member.html', context)


def complete_order(request):
    if request.method == 'GET' and request.is_ajax():
        order_id = int(request.GET['order_id'])

        target_order = order.objects.get(id=order_id)
        target_order.status = 1
        target_order.save()

        return JsonResponse({'status': 1})

def order_received(request):
    if request.method == 'GET' and request.is_ajax():
        order_id = int(request.GET['order_id'])

        target_order = order.objects.get(id=order_id)
        target_order.status = 2
        target_order.save()

        target_credit = credit_cards.objects.get(person=target_order.order_seller)
        target_credit.balance += target_order.total_bill
        target_credit.save() 

        return JsonResponse({'status': 1})






def update_cart(request):
    if request.method == 'GET' and request.is_ajax():
        item_id = int(request.GET['item_id'])
        updated_qty = int(request.GET['updated_qty'])

        target_cart_item = myCart.objects.get(id=item_id)
        target_cart_item.quantity = updated_qty
        target_cart_item.amount = target_cart_item.product.product_price * updated_qty
        target_cart_item.save()

        output = {
            'updated_bill': myCart.objects.filter(buyer=request.user).aggregate(Sum('amount'))['amount__sum'],
            'updated_amount': target_cart_item.amount 
        }
        return JsonResponse(output)

def confirm_order(request):
    output = {}
    if request.method == 'GET' and request.is_ajax():
        confirmed = int(request.GET['confirmed'])

        seller_container = {}

        all_cart_items = myCart.objects.filter(buyer=request.user)

        total_order_amount = myCart.objects.filter(buyer=request.user).aggregate(Sum('amount'))['amount__sum']

        credit_card = credit_cards.objects.get(person=request.user)
        
        user_balance = credit_card.balance

        print('total_order_amount', total_order_amount)
        print('user_balance', user_balance)


        if user_balance >= total_order_amount:

            for i in all_cart_items:
                if i.product.seller not in seller_container.keys():
                    # seller_container.append(i.product.seller)
                    seller_container[i.product.seller] = [i]
                else:
                    seller_container[i.product.seller].append(i)

            print(seller_container)

            for seller in seller_container:
                order_buyer = request.user
                order_seller = seller
                total_items = len(seller_container[seller])
                total_bill = 0
                for i in seller_container[seller]:
                    total_bill += i.amount

                print(order_buyer)
                print(order_seller)
                print(total_items)
                print(total_bill)
                # print(order_buyer)

                new_order = order(
                    order_buyer=order_buyer, 
                    order_seller=order_seller,
                    total_items=total_items,
                    total_bill=total_bill
                )

                new_order.save()

                for i in seller_container[seller]:
                    products_of_order = order_products(product=i.product, quantity=i.quantity, amount=i.amount, parent_order=new_order)
                    products_of_order.save()

            
            credit_card.balance = credit_card.balance - total_order_amount
            credit_card.save()

            output['status'] = 1

            all_cart_items.delete()

                # individual_order = myCart.objects.filter()

        else:
            output['status'] = 0

        return JsonResponse(output)


def delete_cart_item(request):
    if request.method == 'GET' and request.is_ajax():
        item_id = int(request.GET['item_id'])
        
        myCart.objects.get(id=item_id).delete()

    output = {
        'message': "Item has been deleted"
    }
    return JsonResponse(output)

def all_products(request):
    context = {}

    context['all_unis'] = user_more_info.objects.all().values_list('university_name', flat=True)
    context['all_unis'] = list(dict.fromkeys(context['all_unis']))

    context['all_cities'] = user_more_info.objects.all().values_list('city', flat=True)
    context['all_cities'] = list(dict.fromkeys(context['all_cities']))

    print(context['all_unis'])


    if request.user.is_authenticated:
        context['cart_items'] = get_cart_items(request)

 
    all_available_products = []

    all_SELLERS = user_more_info.objects.all()

    if request.method == 'GET':
        if 'university' in request.GET:
            context['filter_uni'] = request.GET['university']
            all_SELLERS.filter(university_name=context['filter_uni'])
            # context['all_products'] = context['all_products'].filter(seller.)

        if 'city' in request.GET:
            context['filter_city'] = request.GET['city']
            all_SELLERS.filter(city=context['filter_city'])

    
    for i in all_SELLERS:
        all_available_products += list(products.objects.filter(seller=i.person))

    print(all_available_products)

    context['all_products'] = all_available_products

    return render(request, 'all_products.html', context)

def all_sellers(request):
    context = {}
    
    if request.user.is_authenticated:
        context['cart_items'] = get_cart_items(request)


    if len(list(user_more_info.objects.all())) > 0:
        context['all_sellers'] = user_more_info.objects.all()

    return render(request, 'all_sellers.html', context)    

def completeProfile(request):
    if request.method == 'POST':
        phone = request.POST['phone']
        city = request.POST['city']
        country = request.POST['country']
        postcode = request.POST['postcode']
        national_id = request.POST['national_id']

        uni_name = request.POST['uni_name']
        uni_id = request.POST['uni_id']
        uni_year = request.POST['uni_year']
        uni_subject = request.POST['uni_subject']

        if not user_more_info.objects.filter(person=request.user).exists():
            more_info = user_more_info(
                person=request.user, 
                phone=phone, 
                city=city,
                country=country,
                postcode=postcode,
                national_id=national_id,
                university_name=uni_name,
                university_id=uni_id,
                university_current_year=uni_year,
                university_subject=uni_subject
            )

            more_info.save()

        # print(phone)
        # print(city)
        # print(country)
        # print(postcode)
        # print(national_id)
        # print(uni_name)
        # print(uni_id)
        # print(uni_year)
        # print(uni_subject)

    return redirect("profile")

def addProduct(request):
    if request.method == 'POST':

        primary_image = request.FILES['image']

        secondary_image1 = ''
        secondary_image2 = ''
        secondary_image3 = ''

        if 'image2' in request.FILES:
            secondary_image1 = request.FILES['image2']

        if 'image3' in request.FILES:
            secondary_image2 = request.FILES['image3']

        if 'image4' in request.FILES:
            secondary_image3 = request.FILES['image4']

        product_name = request.POST['product_name']
        product_price = request.POST['product_price']
        product_tagline = request.POST['product_tagline']
        product_desc = request.POST['product_desc']

        new_product = products(            
            seller=request.user,
            product_primary_image=primary_image,
            product_secondary_image_1=secondary_image1,
            product_secondary_image_2=secondary_image2,
            product_secondary_image_3=secondary_image3,
            product_name=product_name,
            product_tag_line=product_tagline,
            product_price=product_price,
            product_description=product_desc
        )

        new_product.save()

        print(primary_image)
        print(secondary_image1)
        print(secondary_image2)
        print(secondary_image3)

        print(product_name)
        print(product_price)
        print(product_tagline)
        print(product_tagline)

    return redirect("profile")


def add_review(request):
    if request.method == 'POST':
        person_id = request.user
        review_msg = request.POST['myReview']
        product_id = request.POST['productID']
        rating_stars = request.POST['ratings']

        new_rating = product_reviews(author=person_id, review_star=rating_stars, review_msg=review_msg, product=products.objects.get(id=product_id))
        new_rating.save()

    return redirect("product/{}".format(product_id))

def get_cart_items(request):
    if myCart.objects.filter(buyer=request.user).exists():
        return myCart.objects.filter(buyer=request.user).count()
    else:
        return 0

def product(request, id):
    try:
        context = {
            'product': products.objects.get(id=id)
        }

        if product_reviews.objects.filter(product=context['product']).exists():
            context['reviews'] = product_reviews.objects.filter(product=context['product']).order_by("-id")


        if request.method == 'POST':
            product_id = request.POST['product_id']
            qty = int(request.POST['qty'])
            target_product = products.objects.get(id=int(product_id))
            amount = qty * target_product.product_price

            if not myCart.objects.filter(product=target_product, buyer=request.user).exists():
                if request.user != target_product.seller:
                    new_item = myCart(product=target_product, buyer=request.user, quantity=qty, amount=amount)
                    new_item.save()
                    print(product_id)
                    print(qty)
                else:
                    messages.info(request, "You are seller of this product, you can't add it in cart!")

        if request.user.is_authenticated:
            context['credit_status'] = credit_cards.objects.filter(person=request.user).exists()
            context['cart_items'] = get_cart_items(request)
            if myCart.objects.filter(buyer=request.user).exists():
                context['all_cart_items'] = list(myCart.objects.filter(buyer=request.user).values_list('product', flat=True))
                if context['product'].id in context['all_cart_items']:
                    context['added'] = True

        return render(request, 'product.html', context)
    except:
        return redirect("index")


def login(request):

    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(username=email, password=password)
        if user is not None:
            auth.login(request, user)

            if 'next' in request.POST:
                return redirect(request.POST['next'])
            else:
                return redirect("index")
        else:
            messages.info(request, "Incorrect login details!")
            return redirect("login")
    else:
        return render(request, "login.html")

def signup(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        dob = request.POST['dob']
        pic = request.FILES['image']
        context = {
            "name":name,
            "email":email,
            "pass1":pass1,
            "pass2":pass2,
            "dob":dob,
            "pic":pic
        }
        if pass1==pass2:
            if User.objects.filter(username=email).exists():
                print("Email already taken")
                messages.info(request, "Entered email already in use!")
                context['border'] = "email"
                return render(request, "signup.html", context)

            user = User.objects.create_user(username=email, email=dob, first_name=name, password=pass1, last_name=pic)
            user.save()

            user = auth.authenticate(username=email, password=pass1)
            auth.login(request, user)

            save_img = profile_pics(person=request.user, user_img=pic)
            save_img.save()

            send_security_code(request.user, request.user.first_name, request.user.username)

            # return redirect("authentication")
            return redirect("login")

        else:
            messages.info(request, "Your pasword doesn't match!")
            context['border'] = "password"
            return render(request, "signup.html", context)



    return render(request, "signup.html")

def authentication(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            myCode = request.POST['s_code']
            hash_converted = convert_code(myCode)

            thisUserCode = user_confirmation.objects.get(person=request.user)

            if thisUserCode.code_hash == hash_converted:
                thisUserCode.is_verified = True
                thisUserCode.save()
                return redirect("index")
            else:
                messages.info(request, "Entered code is wrong!")

        return render(request, "authentication.html")
    else:
        return redirect("signup")

def send_security_code(u_id, u_name, u_email):
    # generate code
    security_code = generate_code()

    # save in database

    if user_confirmation.objects.filter(person=u_id).exists():
        finding = user_confirmation.objects.filter(person=u_id)
        finding.code_hash = security_code[1]
        finding.is_verified = False
        finding.save()
    else:
        add_confirmation = user_confirmation(person=u_id, code_hash=security_code[1], is_verified=True)
        add_confirmation.save()

    # send email
    # send_html_email(u_name, u_email, security_code[0])

def generate_code():
    CHAR = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    code = ""
    for i in range(0, 6):
        index = randint(0, len(CHAR)-1)
        code += CHAR[index]
    code_hash = hl.md5(code.encode())
    code_hash = code_hash.hexdigest()
    both = (code, code_hash)
    print(both)
    return both

def convert_code(c):
    Hash = hl.md5(c.encode())
    Hash = Hash.hexdigest()
    return Hash

def send_html_email(user_name, user_email, myCode):
    # me == my email address
    # you == recipient's email address
    sender = ''
    receiever = user_email

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Authentication Code"
    msg['From'] = sender
    msg['To'] = user_email

    # Create the body of the message (a plain-text and an HTML version).
    text = "Hello!\nThanks for register on OnlineShopping.com\n"
    html = """\
    <html>
      <head></head>
      <body>
        <p><b>Hello {}!</b><br><br>
           Thanks for register on OnlineShopping.com
           <br>
           Code: <b>{}</b><br>
           Enter the given authentication code in registration form</p>
      </body>
    </html>
    """.format(user_name, myCode)

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part o f a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    # Send the message via local SMTP server.
    mail = smtplib.SMTP('smtp.gmail.com', 587)
    mail.ehlo()
    mail.starttls()
    mail.login(sender, '')
    mail.sendmail(sender, user_email, msg.as_string())
    mail.quit()

def logout(request):
    auth.logout(request)
    return redirect("index")


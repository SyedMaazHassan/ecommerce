from django.db import models
from datetime import datetime
from django.contrib.auth.models import User, auth
# Create your models here.


class user_confirmation(models.Model):
    person = models.ForeignKey(User, on_delete=models.CASCADE)
    code_hash = models.CharField(max_length=32)
    is_verified = models.BooleanField()

class profile_pics(models.Model):
    person = models.ForeignKey(User, on_delete=models.CASCADE)
    user_img = models.ImageField(upload_to='profilePics')

class credit_cards(models.Model):
    person = models.ForeignKey(User, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16)
    cvv_number = models.CharField(max_length=3)
    exp_date = models.DateField()
    balance = models.FloatField(default=5000)

class user_more_info(models.Model):
    person = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=20)
    country = models.CharField(max_length=20)
    postcode = models.CharField(max_length=35)
    national_id = models.CharField(max_length=16)
    university_name = models.CharField(max_length=50)
    university_id = models.CharField(max_length=16)
    university_current_year = models.CharField(max_length=16)
    university_subject = models.CharField(max_length=50)

class products(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    product_primary_image = models.ImageField(upload_to='products')
    product_secondary_image_1 = models.ImageField(upload_to='products', null=True, blank=True)
    product_secondary_image_2 = models.ImageField(upload_to='products', null=True, blank=True)
    product_secondary_image_3 = models.ImageField(upload_to='products', null=True, blank=True)
    product_name = models.CharField(max_length=100)
    product_tag_line = models.CharField(max_length=100)
    product_price = models.FloatField()
    product_description = models.TextField()

class product_reviews(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    review_star = models.IntegerField()
    review_msg = models.TextField()
    product = models.ForeignKey(products, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.today().strftime('%Y-%m-%d'))

class myCart(models.Model):
    product = models.ForeignKey(products, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    amount = models.FloatField()

class order(models.Model):
    order_buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(class)s_this_is_buyer')
    order_seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(class)s_this_is_seller')
    total_items = models.IntegerField()
    total_bill = models.FloatField()
    dateTime = models.DateTimeField(default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    status = models.IntegerField(default=0)

    # 0 for "in process"
    # 1 for "in Delivered"
    # 2 for "in Completed"


class order_products(models.Model):
    product = models.ForeignKey(products, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    amount = models.FloatField()
    parent_order = models.ForeignKey(order, on_delete=models.CASCADE)

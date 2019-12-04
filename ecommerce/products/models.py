from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from decimal import Decimal
from django_countries.fields import CountryField

User = get_user_model()

# --- Choices ---

CATEGORY_CHOICES = (
    ('T', 'Tecnologia'),
    ('BA', 'Bebidas & Alimentos'),
    ('B', 'Belleza'),
    ('M', 'Moda'),
    ('PA', 'Pesca & Aventura'),
    ('H', 'Hobby'),
    ('k', 'Kids'),
    ('G', 'Games'),
    ('D', 'Deportes'),
)

LABEL_CHOICES = (
    ('N', 'Nuevo'),
    ('O', 'Oferta'),
    ('D', 'Destacado')
)

# --- Product Model --- Author: JCVBS

def custom_upload_to(instance, filename):
    old_instance = Product.objects.get(pk = instance.pk)
    old_instance.avatar.delete()

    return 'products/' + filename

class Product(models.Model):
    name = models.CharField(max_length = 100)
    price = models.DecimalField(max_digits = 5, decimal_places = 2, default = 0, validators=[MinValueValidator(Decimal('0.01'))])
    description = models.TextField()
    image = models.ImageField(upload_to = custom_upload_to)
    category = models.CharField(choices = CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices = LABEL_CHOICES, max_length=1)

    class Meta:
        verbose_name = 'producto'
        verbose_name_plural = 'productos'
        ordering = ['name']

    def __str__(self):
        return self.name

# --- Address Model --- Author: JCVBS

class Address(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    street_address = models.CharField(max_length=100)
    country = CountryField(multiple = False, blank_label = '(seleccionar país)')
    zip = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Dirección'
        verbose_name_plural = 'Direcciones'

    def __str__(self):
        return self.user.username

# --- Order Product Model --- Author: JCVBS

class OrderProduct(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    quantity = models.IntegerField(default = 1)

    class Meta:
        verbose_name = 'pedido de producto'
        verbose_name_plural = 'pedido de productos'

    def __str__(self):
        return self.user.username

    def get_total_product_price(self):
        return self.quantity * self.product.price

# --- Order Model --- Author: JCVBS

class Order(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    ordered_products = models.ManyToManyField(OrderProduct)
    order_date = models.DateTimeField(auto_now_add = True)
    ordered = models.BooleanField(default = False)
    address_data = models.ForeignKey(Address, on_delete = models.CASCADE)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'pedido de producto'
        verbose_name_plural = 'pedido de productos'

    def __str__(self):
        return self.user.username

    def get_total_price(self):
        if self.ordered_products.all():
            return sum([ordered_product.product.price for ordered_product in self.ordered_products.all()])

        return None

"""
codigo interesante: analisa

def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })

"""
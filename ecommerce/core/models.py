from django.db import models

# Create your models here.
from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse
from django_countries.fields import CountryField


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

ADDRESS_CHOICES = (
    ('L', 'Local'),
    ('D', 'Delivery'),
)


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Usuario")
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False, verbose_name="Comprar")

    def __str__(self):
        return self.user.username


class Item(models.Model):
    title = models.CharField(max_length=100, verbose_name="Nombre del Producto")
    product_code = models.IntegerField(verbose_name="Condigo del producto")
    price = models.FloatField(verbose_name="Precio")
    discount_price = models.FloatField(blank=True, null=True, verbose_name="Precio de descuento")
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2, verbose_name="Categoria")
    label = models.CharField(choices=LABEL_CHOICES, max_length=1, verbose_name="Clasificacion del producto")
    slug = models.SlugField()
    description = models.TextField(verbose_name="Descripcion")
    description = models.CharField(max_length=200, verbose_name="Descripcion Corta")
    image = models.ImageField(verbose_name="imagen Producto", upload_to="productos/")

    def __str__(self):
        return self.title

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


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, verbose_name="Usuario")
    ref_code = models.CharField(max_length=20, blank=True, null=True, verbose_name="Codigo Referencia")
    items = models.ManyToManyField(OrderItem,verbose_name="Productos")
    start_date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de inicio")
    ordered_date = models.DateTimeField(verbose_name="Fecha de pedido")
    ordered = models.BooleanField(default=False, verbose_name="Comprado")
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Direccion de envio")
    billing_address = models.ForeignKey(
        'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Direccion de factiracion")
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Pago")
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Cupon")
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)


    '''
    1 elemento añadido a la cesta
    2. Agregar una dirección de facturación
    (Falló el pago)
    3. Pago
    (Preprocesamiento, procesamiento, envasado, etc.)
    4. Ser entregado
    5. Recibido
    6. Devoluciones
    '''

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False, blank_label='(seleccionar país)')
    zip = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)
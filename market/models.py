from __future__ import unicode_literals
import os

from django.db import models
from django.conf import settings

from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from versatileimagefield.fields import VersatileImageField
from versatileimagefield.placeholder import OnDiscPlaceholderImage

DEFAULT_KIND_CHOICES = (
    (0, _('Default product'),),
)

PRODUCT_KINDS_CHOICES = getattr(settings, 'MARKET_PRODUCT_KIND_CHOICES', DEFAULT_KIND_CHOICES)


@python_2_unicode_compatible
class Product(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, null=False)
    name = models.CharField(
        _("Name of the product"),
        max_length=300, blank=False, null=False,
    )

    quantity = models.PositiveIntegerField(_("Amount in storage"), default=0, blank=True, null=False)

    image = VersatileImageField(_('product userpic'),
                                blank=True, null=True,
                                upload_to="products/",
                                placeholder_image=OnDiscPlaceholderImage(
                                    path=os.path.join(
                                        os.path.dirname(os.path.abspath(__file__)),
                                        'static/market/img/placeholder.png'
                                    ))
                                )
    status = models.IntegerField(_("product status"), default=1, blank=True, null=False, )

    kind = models.PositiveIntegerField(default=PRODUCT_KINDS_CHOICES[0][0], choices=PRODUCT_KINDS_CHOICES,
                                       blank=True, null=False,)

    created_at = models.DateTimeField(
        _("Created at"),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        _("Updated at"),
        auto_now=True
    )

    active = models.BooleanField(
        _("Active"),
        default=False, help_text=_("Shows whether product is visible to visitors")
    )

    price = models.DecimalField(_("Price"),
                                max_digits=10, blank=False, default=0, null=False, decimal_places=3)

    description = models.TextField(_("product description"), blank=True, null=True)

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return '%s' % (self.name,)


@python_2_unicode_compatible
class Attribute(models.Model):
    name = models.CharField(_("Verbose name of attribute, i.e. Color, Fasion, HDD Size"),
                            max_length=200, blank=False, null=False,)
    key = models.CharField(_('short search key'),
                           max_length=200, blank=False, null=False, unique=True, db_index=True,)

    class Meta:
        verbose_name = _("Product Attribute")
        verbose_name_plural = _("Product Attributes")

    def __str__(self):
        return '%s' % (self.name, )


@python_2_unicode_compatible
class AttributeValue(models.Model):
    """
    This model provides relation between attribute
    and attribute value to particular product.
    """
    product = models.ForeignKey(Product, blank=False, null=False,)
    attribute = models.ForeignKey(Attribute, blank=False, null=False,)
    value = models.CharField(max_length=200, blank=False, null=False)

    class Meta:
        verbose_name = _("Product Attribute Value")
        verbose_name_plural = _("Product Attribute Values")

    def __str__(self):
        return '%s' % (self.name,)


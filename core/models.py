from __future__ import unicode_literals

import os
import random
import string

from django.conf import settings
from django.db import models

from django.core import exceptions
from django.core.urlresolvers import reverse_lazy
from django.core.mail import send_mail

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html
from django.utils.encoding import python_2_unicode_compatible

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth import get_user_model
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin


from django_countries.fields import CountryField

from phonenumber_field.modelfields import PhoneNumberField

from versatileimagefield.fields import VersatileImageField, PPOIField
from versatileimagefield.placeholder import OnDiscPlaceholderImage

from market.models import Product

from messaging.models import Room as MessagingRoom
from jobs.models import CV, Education

from slugify import slugify


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_social_user(self, uid, email, social_name, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        if not email:
            email = "%s@%s.com" % (uid, social_name)
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(''.join([random.choice(string.digits + string.letters) for i in range(0, 10)]))
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, is_social=False, social_name=None, uid=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        if is_social:
            return self.create_social_user(uid, email, social_name, **extra_fields)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Email and password are required. Other fields are optional.
    """

    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    userpic = VersatileImageField(_('profile userpic'),
                                  blank=True, null=True, ppoi_field='userpic_ppoi',
                                  upload_to="customer/userpics",
                                  placeholder_image=OnDiscPlaceholderImage(
                                    path=os.path.join(
                                        os.path.dirname(os.path.abspath(__file__)),
                                        'static/img/steve.jpg'
                                    )))
    userpic_ppoi = PPOIField(
        'Image PPOI'
    )

    phone = PhoneNumberField(_('phone number'), blank=True, null=True, )
    email = models.EmailField(_('email address'), blank=False, null=False, unique=True, )

    birth_date = models.DateField(_("birth date"), blank=True, null=True,)

    country = CountryField(blank=True, null=True)
    state = models.CharField(_("State/region"), max_length=300, blank=True, null=True)
    city = models.CharField(_("city/village"), max_length=300, blank=True, null=True)

    is_email_confirmed = models.BooleanField(_('mail confirmed'), blank=False, null=False, default=False, )
    is_phone_confirmed = models.BooleanField(_('phone confirmed'), blank=False, null=False, default=False, )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )

    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELDS = ['email', 'phone', ]

    # left for django.contrib.auth check
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = False

    @property
    def full_name(self):
        full_name = u'%s %s' % (self.first_name, self.last_name,)
        return full_name.strip()

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = u'%s %s' % (self.first_name, self.last_name,)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)


class BusinessException(Exception):
    pass


class CategoryManager(models.Manager):

    def get_tree(self, as_dict=False):
        """
        Returning categories tree
        """
        all_categories = self.all()
        tmp = dict()
        tree = list()
        for category in all_categories:
            tmp[category.pk] = category
            tmp[category.pk].children = list()
            if category.parent:
                if category.parent.pk in tmp:
                    tmp[category.parent.pk].children.append(category)
                else:
                    tmp[category.parent.pk] = category.parent
                    category.parent.children = [category, ]

        for pk, category in tmp.items():
            if category.parent is None:
                tree.append(category)

        return tree

    def get_tree_json(self):
        """
        Returning categories tree
        """
        all_categories = self.all()
        tmp = dict()
        tree = list()
        for category in all_categories:
            tmp[category.pk] = category
            tmp[category.pk].children = list()
            if category.parent:
                if category.parent.pk in tmp:
                    tmp[category.parent.pk].children.append(category)
                else:
                    tmp[category.parent.pk] = category.parent
                    category.parent.children = [category, ]

        for pk, category in tmp.items():
            if category.parent is None:
                tree.append(category)

        return tree

    def get_serialized_tree(self, serializer_class):
        """
        Returning categories tree
        """
        all_categories = self.all()
        tmp = dict()
        tree = list()
        for category in all_categories:
            serialized_category = serializer_class(instance=category).data
            tmp[category.pk] = serialized_category
            tmp[category.pk]['children'] = list()
            if category.parent:
                if category.parent.pk in tmp:
                    tmp[category.parent.pk]['children'].append(serialized_category)
                else:
                    tmp[category.parent.pk] = serializer_class(instance=category.parent).data
                    tmp[category.parent.pk]['children'] = [serialized_category, ]

        for pk, category in tmp.items():
            if not category['parent']:
                tree.append(category)

        return tree


@python_2_unicode_compatible
class Category(models.Model):
    name = models.CharField(_("Category name"), blank=False, null=False, max_length=200,)
    description = models.TextField(_("About this category"), blank=True, null=True)
    parent = models.ForeignKey('self', blank=True, null=True,)
    icon = VersatileImageField(help_text=_("Category icon"),
                               blank=True,
                               null=True,
                               upload_to="categories/icons",
                               placeholder_image=OnDiscPlaceholderImage(
                                        path=os.path.join(
                                            os.path.dirname(os.path.abspath(__file__)),
                                            'static/img/1.jpg'
                                        )
                               ))
    objects = CategoryManager()

    class Meta:
        verbose_name_plural = _("Categories")
        verbose_name = _("Category")

    def __str__(self):
        return '%s' % (self.name, )


class OrganizationManager(models.Manager):

    def get_company(self, user):
        """
        Since users can have more then one businesses (companies)
        but there is only one main for current user (it have no branches and he is
        handling its administration) this shortcut was written for getting it.
        :param user: settings.AUTH_USER_MODEL
        :return: business.Organization
        """
        try:
            instance = self.get(user=user)
        except exceptions.MultipleObjectsReturned:
            raise BusinessException("User %s has more then one business!" % (user.email, ))
        return instance

    def get_user_related_companies(self, user):
        """
        This method written for getting user related companies,
        where he is an administrator or a staff
        :param user: settings.AUTH_USER_MODEL
        :return: business.Organization queryset
        """
        return self.filter(models.Q(staff__user=user) | models.Q(user=user))


@python_2_unicode_compatible
class Organization(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, null=False)
    slug = models.SlugField(_("Organization url slug"), blank=True, null=False, )

    logo = VersatileImageField(help_text=_("Company logo"),
                                blank=True,
                                null=True,
                                upload_to="company/logo",
                                placeholder_image=OnDiscPlaceholderImage(
                                        path=os.path.join(
                                            os.path.dirname(os.path.abspath(__file__)),
                                            'static/img/1.jpg'
                                        )
                                ))
    image = VersatileImageField(help_text=_("Company page image"),
                                blank=True,
                                null=True,
                                upload_to="company/page",
                                placeholder_image=OnDiscPlaceholderImage(
                                        path=os.path.join(
                                            os.path.dirname(os.path.abspath(__file__)),
                                            'static/img/1.jpg'
                                        )
                                ))
    name = models.CharField(help_text=_("Company name"), max_length=300, blank=False, null=False)
    inn = models.CharField(max_length=300, blank=False, null=False)
    ogrn = models.CharField(max_length=300, blank=False, null=False)
    url = models.URLField(blank=True, null=True)

    messaging_room = models.ForeignKey(MessagingRoom, blank=True, null=True, on_delete=models.SET_NULL)

    country = CountryField(blank=False, null=False)
    state = models.CharField(max_length=300, blank=True, null=True)
    city = models.CharField(max_length=300, blank=True, null=True)

    address_1 = models.CharField(max_length=300, blank=False, null=False)
    address_2 = models.CharField(max_length=300, blank=True, null=True)
    email = models.EmailField(blank=False, null=False)
    phone = PhoneNumberField(blank=False, null=False)
    description = models.TextField(blank=True, null=True)

    date_added = models.DateTimeField(auto_now_add=True, )
    date_modified = models.DateTimeField(auto_now=True, )
    is_confirmed = models.PositiveIntegerField(default=0, blank=False, null=False)
    category = models.ForeignKey(Category, blank=True, null=True)

    objects = OrganizationManager()

    class Meta:
        abstract = False
        verbose_name_plural = _("Organizations")
        verbose_name = _("Organization")

    def __str__(self):
        return '%s (%s, %s)' % (self.name, self.inn, self.country,)

    def get_positive_rating(self):
        return self.rating_set.filter(is_positive=True)

    def get_negative_rating(self):
        return self.rating_set.filter(is_positive=False)

    def get_messaging_room(self):
        if self.messaging_room is None:
            room = MessagingRoom()
            room.save()
            users = get_user_model().objects.filter(staff__organization=self)
            room.users = users
            room.users.add(self.user)
            self.messaging_room = room
            self.save()
        return self.messaging_room

    def get_absolute_url(self):
        return reverse_lazy('organization-view', kwargs={
            'slug': self.slug
        })

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super(Organization, self).save(*args, **kwargs)


@python_2_unicode_compatible
class Partnership(models.Model):
    """
    Many-to-many table which presents partnership
    between organizations. Initiator of partnership is
    "organization", then partner should confirm partnership.
    """
    PARTNERSHIP_STATUS_CHOICES = (
        (0, _('Partnership is not confirmed by partner'), ),
        (1, _('Partnership is confirmed by partner'), ),
        (2, _('Partnership is declined by partner'), ),
    )
    organization = models.ForeignKey(Organization, blank=False, null=False, related_name='organization')
    partner = models.ForeignKey(Organization, blank=False, null=False, related_name='partner')
    status = models.PositiveIntegerField(default=PARTNERSHIP_STATUS_CHOICES[0][0], blank=True,
                                         null=False, choices=PARTNERSHIP_STATUS_CHOICES)

    date_added = models.DateTimeField(auto_now_add=True,)
    date_modified = models.DateTimeField(auto_now=True,)

    def __str__(self):
        return '%s -- %s' % (self.organization, self.partner, )

    class Meta:
        unique_together = ('organization', 'partner', )
        verbose_name = _('Partnership')
        verbose_name_plural = _('Partnerships')


@python_2_unicode_compatible
class Branch(models.Model):
    organization = models.ForeignKey(Organization, blank=False, null=False)

    name = models.CharField(help_text=_("Company name"), max_length=300, blank=False, null=False)

    country = CountryField(blank=False, null=False)
    state = models.CharField(max_length=300, blank=True, null=True)
    city = models.CharField(max_length=300, blank=True, null=True)

    address_1 = models.CharField(max_length=300, blank=False, null=False)
    address_2 = models.CharField(max_length=300, blank=True, null=True)
    email = models.EmailField(blank=False, null=False)
    phone = PhoneNumberField(blank=False, null=False)
    description = models.TextField(blank=True, null=True)

    date_added = models.DateTimeField(auto_now_add=True, )
    date_modified = models.DateTimeField(auto_now=True, )

    objects = OrganizationManager()

    class Meta:
        abstract = False
        verbose_name_plural = _("Branches")
        verbose_name = _("Branch")

    @property
    def full_address(self):
        return "%(country)s %(address_1)s %(city)s" % {
            'country': self.country.name,
            'address_1': self.address_1,
            'address_2': self.address_2,
            'city': self.city,
            'state': self.state,
        }

    def __str__(self):
        return '%s (%s, %s)' % (self.name, self.organization, self.country,)


@python_2_unicode_compatible
class OrganizationProduct(models.Model):
    """
    Many to many represantation of products related to particular organization.
    """
    organization = models.ForeignKey(Organization, blank=False, null=False)
    product = models.ForeignKey(Product, blank=False, null=False)
    category = models.ForeignKey(Category, blank=False, null=False,)

    is_featured = models.BooleanField(_("company featured"), default=False, blank=True, null=False)
    is_popular = models.BooleanField(_("bestseller"), default=False, blank=True, null=False)

    rate_up = models.PositiveIntegerField(_("Green bulb"), default=0, blank=True, null=False)
    rate_down = models.PositiveIntegerField(_("Red bulb"), default=0, blank=True, null=False)
    rate_broken = models.PositiveIntegerField(_("Broken bulb"), default=0, blank=True, null=False)

    def __str__(self):
        return '%s (%s)' % (self.product.name, self.organization.name,)

    @property
    def name(self):
        return self.product.name

    @property
    def price(self):
        return self.product.price

    @property
    def image(self):
        return self.product.image

    @property
    def description(self):
        return self.product.description

    @property
    def kind(self):
        return self.product.kind

    class Meta:
        abstract = False
        unique_together = ('organization', 'product',)


@python_2_unicode_compatible
class Staff(models.Model):
    VERIFICATION_CHOICES = (
        (0, 'Unverified',),
        (1, 'Verified',),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, null=False)
    organization = models.ForeignKey(Organization, blank=True, null=False)
    position = models.CharField(_("position"), max_length=40, blank=True, null=True)
    is_verified = models.PositiveIntegerField(default=VERIFICATION_CHOICES[0][0], blank=True, null=False,)

    date_added = models.DateTimeField(auto_now_add=True, )
    date_modified = models.DateTimeField(auto_now=True, )

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """

        return self.user.get_full_name()

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def email(self):
        return self.user.email

    @property
    def phone(self):
        return self.user.phone

    @property
    def userpic(self):
        return self.user.userpic

    def get_short_name(self):
        "Returns the short name for the user."
        return self.user.first_name

    class Meta:
        abstract = False
        verbose_name = _("Staff")
        verbose_name_plural = _("Staff")

    def __str__(self):
        return '%s, %s' % (self.user.get_full_name(), self.organization.name,)


@python_2_unicode_compatible
class Vacancy(models.Model):
    organization = models.ForeignKey(Organization, blank=False, null=False, related_name='vacancies')

    name = models.CharField(_("Vacancy position name"), max_length=300, blank=False, null=False,)

    description = models.TextField(_("Extended description"), blank=False, null=False)
    cv = models.ForeignKey(CV, blank=False, null=False)

    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = False
        verbose_name = _("Vacancy")
        verbose_name_plural = _("Vacancies")

    def get_html(self):
        return format_html(self.text)

    def __str__(self):
        return '%s' % (self.name, )

    @property
    def specialization(self):
        # TODO: check sql requests
        if self.cv.education_set.first():
            return self.cv.education_set.first().specialization
        return None

    @property
    def degree(self):
        # TODO: check sql requests
        if self.cv.education_set.first():
            return self.cv.education_set.first().degree
        return None

    @property
    def degree_verbose(self):
        # TODO: check sql requests
        if self.cv.education_set.first():
            return Education.EDUCATION_DEGREE_CHOICES[self.cv.education_set.first().degree][1]
        return None

    @property
    def skills(self):
        # TODO: check sql requests
        return self.cv.skill_set.all()

    @property
    def languages(self):
        # TODO: check sql requests
        return self.cv.language_set.all()

    @staticmethod
    def degree_choices():
        # TODO: check sql requests
        return Education.EDUCATION_DEGREE_CHOICES


@python_2_unicode_compatible
class HTMLWidgetModel(models.Model):
    DEFAULT_TEXT = ""
    text = models.TextField(blank=False, null=True, default=DEFAULT_TEXT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, null=False)
    slug = models.TextField(max_length=200, blank=False, null=False, db_index=True)

    class Meta:
        abstract = False
        verbose_name = _("HTML Widget")
        verbose_name_plural = _("HTML Widgets")
        unique_together = ("user", "slug", )

    def get_html(self):
        return format_html(self.text)

    def __str__(self):
        return '%s' % (self.slug, )


@python_2_unicode_compatible
class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, null=False, related_name="author")
    text = models.TextField(blank=False, null=False)
    organization = models.ForeignKey(Organization, blank=False, null=False)

    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    updated_at = models.DateTimeField(auto_now=True, blank=False, null=False)

    def __str__(self):
        return "%s (%s)" % (self.organization.name, self.user.email, )


@python_2_unicode_compatible
class VisitorMessage(models.Model):
    VISITOR_MESSAGE_SEND_TO_CHOICES = (
        (0, _("Send to organization page"),),
        (1, _("Send to organization email"),),
    )
    PHONE_STATUS_CHOICES = (
        (0, _("Phone is not verified"),),
        (1, _("Phone is verified"),),
        (2, _("Verification was sent"),),
    )
    EMAIL_STATUS_CHOICES = (
        (0, _("Email is not verified"),),
        (1, _("Email is verified"),),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, help_text=_("Authed user id"),)
    sender_name = models.CharField(max_length=200, blank=True, null=True,)
    email = models.EmailField(blank=False, null=False, help_text=_("Email to reply"),)
    phone = PhoneNumberField(blank=True, null=True, help_text=_("Phone for callback"),)
    text = models.TextField(blank=False, null=False)
    ip = models.CharField(max_length=200, blank=True, null=True, help_text=_("IP from which message was sent"))
    organization = models.ForeignKey(Organization, blank=False, null=False)

    send_to = models.PositiveIntegerField(_("Kind of submited message"), default=0, blank=True, null=False,
                                             choices=VISITOR_MESSAGE_SEND_TO_CHOICES)
    is_deleted = models.BooleanField(default=False, blank=True, null=False,)
    is_confirmed = models.BooleanField(default=False, blank=True, null=False,)

    phone_status = models.PositiveIntegerField(default=0, blank=True, null=False,
                                               choices=PHONE_STATUS_CHOICES)
    email_status = models.PositiveIntegerField(default=0, blank=True, null=False,
                                               choices=EMAIL_STATUS_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    updated_at = models.DateTimeField(auto_now=True, blank=False, null=False)

    def __str__(self):
        return "%s (%s)" % (self.organization.name, self.user or self.email or self.phone, )


class RatingManager(models.Manager):
    def vote(self, user, organization, is_positive):
        """
        Creates or changes user vote
        :param user: settings.AUTH_USER_MODEL
        :param organization: Organization
        :param is_positive: Boolean
        :return: Rating
        """
        try:
            rating = self.get(user=user, organization=organization)
        except exceptions.ObjectDoesNotExist:
            rating = self.create(user=user, organization=organization, is_positive=is_positive)
        else:
            if rating.is_positive != is_positive:
                rating.is_positive = is_positive
                rating.save()
        return rating


@python_2_unicode_compatible
class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=False, )
    organization = models.ForeignKey(Organization, blank=False, null=False, )
    is_positive = models.BooleanField(blank=False, null=False, )

    objects = RatingManager()

    class Meta:
        unique_together = ('user', 'organization', )
        verbose_name = _("Rating")
        verbose_name_plural = _("Ratings")

    def __str__(self):
        return "%s voted %s for %s" % (self.user,
                                       _("positive") if self.is_positive else _("negative"),
                                       self.organization,)

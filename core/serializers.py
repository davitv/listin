import os
import magic

from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.core.files import File
from django.contrib.auth import (
    password_validation,
)

from rest_framework import serializers
from versatileimagefield.serializers import VersatileImageFieldSerializer
from django_countries.serializer_fields import CountryField

from utils.serializers import ConcatenatedListField
from utils.files import (
    get_file_by_path, get_file_by_url, validate_file_url
)

from market.serializers import ProductSerializer
from core.models import (
    Organization, Branch, Comment, Category,
    Staff, Vacancy, Rating, VisitorMessage,
    OrganizationProduct, User
)
from jobs.models import Skill, CV, Language, Education


class VersatileImageFieldPathSerializer(VersatileImageFieldSerializer):
    def to_internal_value(self, data):
        file_object = super(VersatileImageFieldPathSerializer, self).to_internal_value(data)
        return file_object


class UserSerializer(serializers.ModelSerializer):
    userpic = VersatileImageFieldPathSerializer(
        sizes=[
            ('full_size', 'url'),
            ('thumbnail', 'crop__100x100'),
            ('medium_square_crop', 'crop__600x600'),
        ]
    )
    userpic_url = serializers.CharField(required=False, validators=[validate_file_url, ])
    country = CountryField()

    def validate_userpic_url(self, value):
        f = get_file_by_path(value) or get_file_by_url(value)
        if not f:
            raise serializers.ValidationError("Please, submit correct file path")
        self.fields['userpic'].value = f
        return File(f)

    def validate(self, data):
        return data

    @staticmethod
    def get_size(size, instance):
        if size == 'url':
            return instance.url
        kind, size = size.split("__")
        return getattr(instance, kind)[size].url

    def to_representation(self, instance):
        data = super(UserSerializer, self).to_representation(instance)
        if not data['userpic']:
            data['userpic'] = dict(
                map(lambda args: (args[0], self.get_size(args[1], instance.userpic),),
                    self.fields['userpic'].sizes)
            )
        return data

    def update(self, instance, validated_data):
        serializers.raise_errors_on_nested_writes('update', self, validated_data)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if validated_data.get('userpic_url'):
            image = validated_data.get('userpic_url')
            name = os.path.basename(validated_data.get('userpic_url').name)
            instance.userpic.save(name, image, True)
        instance.save()

        return instance

    class Meta:
        model = User
        exclude = (
            'password',
            'last_login',
            'is_active',
            'is_superuser',
            'is_staff',
            'date_joined',
            'groups',
            'user_permissions',
        )


class UserRegistrationSerializer(serializers.ModelSerializer):
    default_error_messages = {
        'password_mismatch': "Entered passwords are not matching"
    }

    userpic = VersatileImageFieldSerializer(
        required=False,
        allow_empty_file=True,
        sizes=[
            ('full_size', 'url'),
            ('thumbnail', 'thumbnail__100x100'),
            ('medium_square_crop', 'crop__600x600'),
        ]
    )
    password = serializers.CharField(label=_("Password"))

    @staticmethod
    def get_size(size, instance):
        if size == 'url':
            return instance.url
        kind, size = size.split("__")
        return getattr(instance, kind)[size].url

    def validate_password(self, value):
        password_validation.validate_password(value, self.instance)
        return value

    def to_representation(self, instance):
        data = super(UserRegistrationSerializer, self).to_representation(instance)
        if not data['userpic']:
            data['userpic'] = dict(
                map(lambda args: (args[0], self.get_size(args[1], instance.userpic),),
                    self.fields['userpic'].sizes)
            )
        return data

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'phone',
            'password',
            'userpic',
        )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category

    icon = VersatileImageFieldSerializer(
        required=False,
        sizes=[
            ('full_size', 'url'),
            ('thumbnail', 'thumbnail__150x150'),
            ('medium_square_crop', 'crop__555x238'),
        ]
    )

    @staticmethod
    def get_size(size, instance):
        if size == 'url':
            return instance.url
        kind, size = size.split("__")
        return getattr(instance, kind)[size].url

    def to_representation(self, instance):
        data = super(CategorySerializer, self).to_representation(instance)

        if not data['icon']:
            data['icon'] = dict(
                map(lambda args: (args[0], self.get_size(args[1], instance.icon),),
                    self.fields['icon'].sizes)
            )
        return data


class VacancySerializer(serializers.ModelSerializer):
    default_error_messages = {
        'education_value_missing': _('Education value is incomplete')
    }

    class Meta:
        model = Vacancy
        exclude = (
            'cv',
        )

    skills = ConcatenatedListField(required=False, child=serializers.CharField(), to_repr=lambda x: x.name)
    languages = ConcatenatedListField(required=False, child=serializers.CharField(), to_repr=lambda x: x.name)
    specialization = serializers.CharField(required=False, )
    degree = serializers.IntegerField(required=False, )
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all(), required=True, )

    def validate(self, attrs):
        specialization = attrs.get('specialization', False)
        degree = attrs.get('degree', False)
        try:
            assert (specialization and degree) or not (specialization or degree)
        except AssertionError:
            raise serializers.ValidationError(self.default_error_messages['education_value_missing'])

        if degree == 0:
            attrs.pop('degree')

        try:
            user = self.context['user']
        except KeyError:
            pass
        else:
            attrs['user'] = user

        return attrs

    def create(self, validated_data):
        cv = CV.objects.create(user=validated_data.pop('user'))
        skills = [Skill.objects.create(name=name, cv=cv) for name in validated_data.pop('skills', [])]
        languages = [Language.objects.create(name=name, cv=cv) for name in validated_data.pop('languages', [])]
        if validated_data.get('specialization', False):
            education = Education.objects.create(
                specialization=validated_data.pop('specialization'),
                degree=validated_data.pop('degree'),
                cv=cv
            )
        validated_data.pop('degree', False)
        validated_data['cv'] = cv
        instance = super(VacancySerializer, self).create(validated_data)
        return instance

    def update(self, instance, validated_data):
        cv = instance.cv

        if validated_data.get('specialization', False):
            try:
                education = Education.objects.get(cv=cv)
            except Education.DoesNotExist:
                # we can safely create education instance in this case
                Education.objects.create(
                    specialization=validated_data.pop('specialization'),
                    degree=validated_data.pop('degree'),
                    cv=cv
                )
            else:
                education.specialization = validated_data.pop('specialization')
                education.degree = validated_data.pop('degree')
                education.save()

        # now we need to clean skills and languages which
        # has been saved previously but not presented in
        # current data
        skills = [Skill.objects.get_or_create(name=name, cv=cv)[0] for name in validated_data.pop('skills', [])]
        languages = [Language.objects.get_or_create(name=name, cv=cv)[0] for name in
                     validated_data.pop('languages', [])]

        for s in Skill.objects.filter(cv=cv):
            if s not in skills:
                s.delete()

        for l in Language.objects.filter(cv=cv):
            if l not in languages:
                l.delete()

        validated_data['cv'] = cv
        instance = super(VacancySerializer, self).update(instance, validated_data)
        return instance


class OrganizationVacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = ("id",)


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        exclude = (
            "user",
            "is_confirmed",
        )

    url = serializers.SerializerMethodField()
    vacancies_url = serializers.SerializerMethodField()
    visitor_message_url = serializers.SerializerMethodField()
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=True)
    vacancies = OrganizationVacancySerializer(read_only=True, many=True)
    full_address = serializers.SerializerMethodField()

    image = VersatileImageFieldSerializer(
        required=False,
        sizes=[
            ('full_size', 'url'),
            ('thumbnail', 'thumbnail__150x150'),
            ('medium_square_crop', 'crop__555x238'),
        ]
    )

    logo = VersatileImageFieldSerializer(
        required=False,
        sizes=[
            ('full_size', 'url'),
            ('thumbnail', 'thumbnail__150x150'),
            ('medium_square_crop', 'crop__555x238'),
        ]
    )

    logo_url = serializers.CharField(write_only=True, required=False, validators=[validate_file_url, ])

    def validate(self, attrs):
        try:
            user = self.context['user']
        except KeyError:
            pass
        else:
            attrs['user'] = user
        logo = attrs.pop('logo_url', None)
        if logo:
            attrs['logo'] = File(logo)
        try:
            user = self.context.get('user', None)
            assert user
        except AssertionError:
            raise serializers.ValidationError("Serilizer should be called with user context")
        else:
            attrs['user'] = user
        return attrs

    def validate_logo_url(self, value):
        f = get_file_by_path(value) or get_file_by_url(value)
        if not f:
            raise serializers.ValidationError("Please, submit correct file path")
        return f

    def get_url(self, obj):
        return obj.get_absolute_url()

    def get_vacancies_url(self, obj):
        return reverse_lazy('organization-vacancies', kwargs={
            'slug': obj.slug
        })

    def get_visitor_message_url(self, obj):
        return reverse_lazy('api-visitor-message', kwargs={
            'organization_pk': obj.pk
        })

    def to_representation(self, instance):
        ret = super(OrganizationSerializer, self).to_representation(instance)
        if instance.category is not None:
            ret['category'] = instance.category.name
        return ret

    def get_full_address(self, obj):
        return "%s %s %s %s %s" % (obj.country.name, obj.state, obj.city, obj.address_1, obj.address_2)


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        exclude = (
            'organization',
        )
    full_address = serializers.SerializerMethodField()

    def get_full_address(self, obj):
        return "%s %s %s %s %s" % (obj.country.name, obj.state, obj.city, obj.address_1, obj.address_2)

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all(), write_only=True,)

    class Meta:
        model = Comment

    def save(self, **kwargs):
        return super(CommentSerializer, self).save(user=self.context['user'])


class StaffSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    def to_representation(self, instance):
        """
        Overrided this method for getting object that
        is looks like UserSerializer with few additional
        staff related fields. Returned instance id is NOT
        staff id, it's settings.AUTH_USER_MODEL id.
        """
        ret = super(StaffSerializer, self).to_representation(instance)
        ret = ret['user']
        ret['position'] = instance.position
        return ret

    class Meta:
        model = Staff
        exclude = (
            'organization',
            'date_added',
            'date_modified',
        )


class RatingSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    organization = OrganizationSerializer()

    class Meta:
        model = Rating


class RatingResponseSerializer(serializers.Serializer):
    total = serializers.IntegerField(default=0, read_only=True)
    positive = serializers.IntegerField(default=0, read_only=True)
    negative = serializers.IntegerField(default=0, read_only=True)

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True, write_only=True, )
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        required=True,
        write_only=True,
    )
    is_positive = serializers.BooleanField(required=True, write_only=True)

    def save(self, **kwargs):
        rating = Rating.objects.vote(
            self.validated_data['user'],
            self.validated_data['organization'],
            self.validated_data['is_positive']
        )


class TempFileUploadSerializer(serializers.Serializer):
    file = VersatileImageFieldSerializer(required=True, sizes=[
        ('full_size', 'url'),
        ('thumbnail', 'thumbnail__150x150'),
        ('medium_square_crop', 'crop__555x238'),
    ])
    mime_type = None

    def create(self, validated_data):
        file = validated_data['file']
        mime = magic.from_buffer(file.read(1024), mime=True)
        file.seek(0)
        filename = os.path.basename(file.file.name)
        return {
            'url': os.path.join(settings.TEMP_FILES_URL, filename),
            'mime': mime,
            'name': filename
        }


class VisitorMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitorMessage
        exclude = (
            'email_status',
            'phone_status',
            'is_deleted',
            'is_confirmed',
            'user',
            'ip',
        )

    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all(), required=False)
    default_error_messages = {
        'permission_denied': _("You should be authorized to use this method."),
        'wrong_organization_data': _("Organization info is missing or incorrect"),
    }

    def validate(self, attrs):
        if not attrs.get('organization', False):
            try:
                attrs['organization'] = Organization.objects.get(pk=self.context.get('organization', 0))
            except Organization.DoesNotExist:
                raise serializers.ValidationError(self.default_error_messages['wrong_organization_data'])
        return attrs

    def create(self, validated_data):
        instance = super(VisitorMessageSerializer, self).create(validated_data)
        if 'user' in self.context:
            instance.user = self.context['user']
            instance.email_status = int(
                (validated_data.get('email', None) == instance.user.email) and instance.user.is_email_confirmed
            )
            instance.phone_status = int(
                (validated_data.get('phone', None) == instance.user.phone) and instance.user.is_phone_confirmed
            )
        return instance


class _OrganizationProductSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all(), required=True, )
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=True, )

    class Meta:
        model = OrganizationProduct
        exclude = (
            'product',
        )


class OrganizationProductSerializer(ProductSerializer):
    organization = serializers.IntegerField(required=True, write_only=True)
    category = serializers.IntegerField(required=True, write_only=True)
    is_featured = serializers.BooleanField(required=False, write_only=True)
    is_popular = serializers.BooleanField(required=False, write_only=True)
    organization_data = (
        'organization',
        'category',
        'is_featured',
        'is_popular',
    )

    organization_product_serializer = None
    organization_product_instance = None
    default_error_messages = {
        'inconsistent_product_state': _(
            "Some strange error occurred. We are working to fix it. Please, contact to administration")
    }

    def validate(self, attrs):
        if self.instance:
            # try to find existing OrganizationProduct instance
            # since organization and product are unique together
            # we can query it with get function
            try:
                self.organization_product_instance = OrganizationProduct.objects.get(
                    organization=attrs.get('organization'),
                    product=self.instance
                )
            except OrganizationProduct.DoesNotExist:
                # we have a product instance but don't
                # have any OrganizationProduct related to it
                # basically, this is strange and should not pass silently
                # so just raise exception
                raise serializers.ValidationError(self.default_error_messages['default_error_messages'])

        organization_data = dict()
        for name in self.organization_data:
            if name in attrs:
                organization_data[name] = attrs.pop(name)

        self.organization_product_serializer = _OrganizationProductSerializer(
            data=organization_data, instance=self.organization_product_instance
        )

        self.organization_product_serializer.is_valid(True)
        return attrs

    def save(self, **kwargs):
        product = super(OrganizationProductSerializer, self).save(user=self.context['user'])
        self.organization_product_serializer.save(product=product)
        return product

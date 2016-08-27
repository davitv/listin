from django import forms

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.files import File
from django.utils.translation import ugettext_lazy as _
from django.utils.text import capfirst

from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.hashers import check_password
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)

from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from versatileimagefield.forms import VersatileImageFormField

from core.widgets import PreviewImageWidget
from core.models import (
    User, Organization, Comment, Product,
    Staff, VisitorMessage, OrganizationProduct,
    Vacancy, BusinessException, Branch, Category
)

from jobs.models import CV, Language, Skill, Education


class PhoneNumberPrefixWidgetFixed(PhoneNumberPrefixWidget):
    def value_from_datadict(self, data, files, name):
        values = super(PhoneNumberPrefixWidget, self).value_from_datadict(
            data, files, name)
        return '%s%s' % tuple(values)


class AdminUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label=_("Password"),
        help_text=_("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"../password/\">this form</a>."))
    userpic = VersatileImageFormField(required=False)
    phone = PhoneNumberField(required=False)

    class Meta(object):
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(AdminUserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions')
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class TempFileInputWidget(forms.ClearableFileInput):
    default_error_messages = {
        'invalid_image': _(
            "Upload a valid image. The file you uploaded was either not an "
            "image or a corrupted image."
        ),
    }

    def value_from_datadict(self, data, files, name):
        upload = super(TempFileInputWidget, self).value_from_datadict(data, files, name)
        if upload is None and data.get(name, False):
            tmp_file = File(open(data.get(name, False), 'r'))
            return tmp_file
        return upload

    def to_python(self, data):
        """
        Checks that the file-upload field data contains a valid image (GIF, JPG,
        PNG, possibly others -- whatever the Python Imaging Library supports).
        """
        return super(TempFileInputWidget, self).to_python(data)


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label=_("Password"),
        help_text=_("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"../password/\">this form</a>."))
    userpic = forms.ImageField(required=False, widget=TempFileInputWidget)
    phone = PhoneNumberField(required=False,)

    class Meta(object):
        model = User
        exclude = ('is_staff',
                   'is_active',
                   'is_email_confirmed',
                   'is_phone_confirmed',
                   'userpic_ppoi',
                   'date_joined',
                   'is_superuser',
                   'groups',
                   'user_permissions',
                   'last_login',
                   )

    def __init__(self, request, *args, **kwargs):
        super(UserChangeForm, self).__init__(instance=request.user, *args, **kwargs)
        self.request = request
        f = self.fields.get('user_permissions')
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_userpic(self):
        value = self.cleaned_data['userpic']
        return value

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

    def as_milligram(self):
        "Returns this form rendered as HTML <p>s."
        return self._html_output(
            normal_row='<p%(html_class_attr)s>%(label)s %(field)s%(help_text)s</p>',
            error_row='%s',
            row_ender='</p>',
            help_text_html=' <span class="helptext">%s</span>',
            errors_on_separate_row=True)


class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    user_cache = None
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as before, for verification."))

    class Meta:
        model = User
        fields = ("email", )

    def send_confirmation_mail(self):
        import helpers
        helpers.send_email_confirmation(self.user_cache)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        self.instance.username = self.cleaned_data.get('username')
        password_validation.validate_password(self.cleaned_data.get('password2'), self.instance)
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            self.user_cache = user
            if settings.AUTH_MAIL_CONFIRMATION:
                self.send_confirmation_mail()
        return user


class AuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    username = forms.CharField(max_length=254)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': _("Please enter a correct %(username)s and password. "
                           "Note that both fields may be case-sensitive."),
        'inactive': _("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super(AuthenticationForm, self).__init__(*args, **kwargs)

        # Set the label for the "username" field.
        UserModel = get_user_model()
        self.username_field = UserModel._meta.get_field(UserModel.USERNAME_FIELD)
        if self.fields['username'].label is None:
            self.fields['username'].label = capfirst(self.username_field.verbose_name)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username,
                                           password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a
        ``forms.ValidationError``.

        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class PasswordResetForm(forms.Form):
    email = forms.EmailField(label=_("Email"), max_length=254)

    @staticmethod
    def get_users(email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        active_users = get_user_model()._default_manager.filter(
            email__iexact=email, is_active=True)
        return (u for u in active_users if u.has_usable_password())

    def save(self):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        email = self.cleaned_data["email"]
        for user in self.get_users(email):
            import helpers
            helpers.send_password_reset_email(user)


class SetPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    new_password1 = forms.CharField(label=_("New password"),
                                    widget=forms.PasswordInput,
                                    help_text=password_validation.password_validators_help_text_html())
    new_password2 = forms.CharField(label=_("New password confirmation"),
                                    widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        password_validation.validate_password(password2, self.user)
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class SetNewPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """
    user_cache = None
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
        'wrong_current_password': _("Wrong current password"),
    }
    current_password = forms.CharField(label=_("Current password"),
                                       widget=forms.PasswordInput)
    new_password1 = forms.CharField(label=_("New password"),
                                    widget=forms.PasswordInput,
                                    help_text=password_validation.password_validators_help_text_html())
    new_password2 = forms.CharField(label=_("New password confirmation"),
                                    widget=forms.PasswordInput)

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(SetNewPasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        password_validation.validate_password(password2, self.request.user)
        return password2

    def clean_current_password(self):
        password = self.cleaned_data.get('current_password')
        if not check_password(password, self.request.user.password,):
            raise forms.ValidationError(
                self.error_messages['wrong_current_password'],
                code='wrong_password'
            )
        return password

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user_cache = self.request.user
        self.user_cache.set_password(password)
        if commit:
            self.user_cache.save()
        return self.user_cache

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        exclude = (
            "user",
            "is_confirmed",
            "rate_up",
            "rate_down",
            "rate_broken",
        )

    def __init__(self, user, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)
        self.user_cache = user

    def save(self, commit=True):
        instance = super(OrganizationForm, self).save(commit=False)
        instance.user = self.user_cache
        if commit:
            instance.save()
        return instance


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = '__all__'
    organization = forms.IntegerField(required=False, )

    error_messages = {
        'illegal_organization_access': _("Sorry, you have no rights to add branch for this organization"),
        'wrong_organization_pk': _("Organization was not found."),
    }

    def __init__(self, user, *args, **kwargs):
        super(BranchForm, self).__init__(*args, **kwargs)
        self.user_cache = user

    def clean_organization(self):
        pk = self.cleaned_data.get('organization')
        try:
            organization = Organization.objects.get(pk=pk)
            assert organization.user == self.user_cache
        except AssertionError:
            raise forms.ValidationError(
                self.error_messages['illegal_organization_access'],
                'illegal_organization_access'
            )
        except ObjectDoesNotExist:
            raise forms.ValidationError(
                self.error_messages['wrong_organization_pk'],
                'illegal_organization_access'
            )
        return organization

    def clean(self):
        data = self.cleaned_data
        organization = data.get('organization', False)
        if not organization:
            data['organization'] = Organization.objects.filter(user=self.user_cache).first()
        return data


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = (
            "user",
            "rate_up",
            "rate_down",
            "rate_broken",
            "business",
        )
    image = forms.ImageField(required=False, widget=PreviewImageWidget())
    is_featured = forms.BooleanField(required=False)
    is_popular = forms.BooleanField(required=False)
    is_project = forms.BooleanField(required=False)
    is_service = forms.BooleanField(required=False)
    category = forms.IntegerField(required=True)

    def __init__(self, user, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.user_cache = user

    def save(self, commit=True):
        instance = super(ProductForm, self).save(commit=False)
        instance.user = self.user_cache
        if commit:
            instance.status = 1
            instance.save()
            organization = Organization.objects.filter(user=self.user_cache).first()
            try:
                organization_product = OrganizationProduct.objects.get(organization=organization,
                                                                       product=instance)
            except ObjectDoesNotExist:
                organization_product = OrganizationProduct(
                    organization=organization,
                    product=instance,
                )
            organization_product.category = Category.objects.get(pk=self.cleaned_data.get("category", False))
            organization_product.is_featured = self.cleaned_data.get("is_featured", False)
            organization_product.is_popular = self.cleaned_data.get("is_popular", False)
            organization_product.is_project = self.cleaned_data.get("is_project", False)
            organization_product.is_service = self.cleaned_data.get("is_service", False)
            organization_product.save()
        return instance


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = (
            "user",
        )

    def __init__(self, user, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.user_cache = user

    def save(self, commit=True):
        instance = super(CommentForm, self).save(commit=False)
        instance.user = self.user_cache
        if commit:
            instance.save()
        return instance


class StaffForm(forms.ModelForm):
    first_name = forms.CharField(required=True, )
    last_name = forms.CharField(required=True, )
    email = forms.EmailField(required=True, )
    phone = PhoneNumberField(required=False, )
    position = forms.CharField(required=True, )
    user = forms.IntegerField(required=False, )

    error_messages = {
        'system_error': _("Sorry. Some system error has been occured. Administration is already notified"),
        'different_users': _("We have registered two different users with those email and phone"),
        'already_exists': _("This person is already listed in the staff of your company."),
        'invite_already_sent': _("You have already sent staff invitation for this person. He havent't"
                                 "accept it yet though."),
    }

    class Meta:
        model = Staff
        fields = "__all__"

    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.business = Organization.objects.get_company(user)

        self.user_cache_email = None
        self.user_cache_phone = None
        self.user_cache = None

        super(StaffForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            user = get_user_model().objects.get(email=email)
        except ObjectDoesNotExist:
            pass
        else:
            self.user_cache_email = user
        return email

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        try:
            # phone is optional, no need to query if it's None
            assert phone
            user = get_user_model().objects.get(phone=phone)
        except (ObjectDoesNotExist, AssertionError,):
            pass
        else:
            self.user_cache_phone = user
        return phone

    def clean(self):
        data = self.cleaned_data
        data['organization'] = self.business
        if self.user_cache_email and self.user_cache_phone:
            # we have registered user/users with phone and
            # email, so need to be sure it's same user
            if self.user_cache_phone != self.user_cache_email:
                raise forms.ValidationError(
                    self.error_messages['different_users'],
                    'different_users'
                )
            else:
                self.user_cache = self.user_cache_phone
        else:
            self.user_cache = self.user_cache_phone or self.user_cache_email

        if self.user_cache is None:
            # couldn't find any user with those data in db,
            # so lets create new one
            self.user_cache = get_user_model()(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                phone=data.get("phone", None),
            )
            self.user_cache.set_password(get_user_model().objects.make_random_password())
            self.user_cache.save()
        else:
            # we need to check if this person was already
            # added or invited as staff and forbid to invite
            # him again or adding two times
            try:
                staff = Staff.objects.get(organization=self.business, user=self.user_cache)
            except ObjectDoesNotExist:
                # everything is fine, he is not a staff for
                # for this organization
                pass
            except MultipleObjectsReturned:
                # this exception should never raise
                # added DB ability to save multiple staff
                # rows for same organization only for future purposes
                raise forms.ValidationError(
                    self.error_messages['system_error'],
                    'system_error',
                )
            else:
                # he is a staff, or already been invited
                if staff.is_verified:
                    raise forms.ValidationError(
                        self.error_messages['already_exists'],
                        'already_exists',
                    )
                else:
                    raise forms.ValidationError(
                        self.error_messages['invite_already_sent'],
                        'invite_already_sent',
                    )
        data['user'] = self.user_cache
        return data

    def save(self, commit=True):
        staff = Staff(
            user=self.user_cache,
            organization=self.business,
            position=self.cleaned_data['position'],
            is_verified=False,
        )
        if commit:
            staff.save()
        return staff


class VisitorMessageForm(forms.ModelForm):
    class Meta:
        model = VisitorMessage
        exclude = (
            "ip",
            "user",
        )
    error_messages = {
        'organization_not_found': _("Organization with that id doesn't exists"),
    }

    def __init__(self, request, *args, **kwargs):
        self.request = request
        self.business = Organization.objects.get_company(request.user)
        super(VisitorMessageForm, self).__init__(*args, **kwargs)

    def clean(self):
        data = self.cleaned_data
        # TODO: get and save IP
        if self.request.user.is_authenticated():
            data['user'] = self.request.user
        return data

    def clean_organization(self):
        organization_id = self.cleaned_data['organization']
        try:
            organization = Organization.objects.get(pk=organization_id)
        except ObjectDoesNotExist:
            raise forms.ValidationError(
                self.error_messages['organization_not_found'],
                'organization_not_found'
            )
        return organization


class VacancyForm(forms.ModelForm):
    name = forms.CharField(help_text=_("Vacancy name"), required=True, )
    description = forms.CharField(help_text=_("About work"), required=True, )

    speciality = forms.CharField(help_text=_("education speciality"), required=False, )
    degree = forms.ChoiceField(help_text=_("speciality degree"),
                               choices=Education.EDUCATION_DEGREE_CHOICES,
                               required=False,
                               )

    skills = forms.CharField(required=False, )
    languages = forms.CharField(required=False, )

    class Meta:
        model = Vacancy
        exclude = ("user", "organization", "cv",)

    def __init__(self, user, *args, **kwargs):
        self.user_cache = user

        try:
            self.organization = Organization.objects.get_company(user)
        except ObjectDoesNotExist:
            raise BusinessException(_("User needs to have a registered organization for using this form"))
        super(VacancyForm, self).__init__(*args, **kwargs)

    def clean_skills(self):
        if getattr(self.data, 'getlist', False):
            return [skill.strip() for skill in self.data.getlist('skills', []) if len(skill.strip())]
        return [skill.strip() for skill in self.data['skills'].split(',') if len(skill.strip())]

    def clean_languages(self):
        if getattr(self.data, 'getlist', False):
            return [name.strip() for name in self.data.getlist('languages', []) if len(name.strip())]
        return [name.strip() for name in self.data['languages'].split(',') if len(name.strip())]

    def get_languages(self, langs=None):
        if langs:
            return
        return []

    def get_education(self, speciality, degree):
        data = self.cleaned_data
        return data

    def clean(self):
        data = self.cleaned_data

        data['skills'] = [Skill(name=name, level=0) for name in data.get('skills', [])]

        data['languages'] = [Language(name=name, level=0) for name in data.get('languages', [])]

        data['education'] = Education(
            specialization=data['speciality'],
            degree=data['degree']
        )

        return data

    def save(self, organization=None):
        data = self.cleaned_data

        cv = CV(
            user=self.user_cache
        )
        cv.save()
        for skill in data.get('skills', []):
            skill.cv = cv
            skill.save()

        for language in data.get('languages', []):
            language.cv = cv
            language.save()

        data['education'].cv = cv
        data['education'].save()

        self.instance.organization = self.organization
        self.instance.cv = cv
        self.instance.save()
        return self.instance

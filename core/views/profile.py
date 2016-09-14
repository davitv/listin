import os

from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.conf import settings

from django.core.urlresolvers import reverse_lazy

from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from django.views.generic import FormView, RedirectView, TemplateView

from django.contrib.auth import (
    login as auth_login,
    logout as auth_logout,
    get_user_model,
)
from django.contrib.auth.tokens import default_token_generator

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

from core.forms import (
    UserCreationForm, SetNewPasswordForm, AuthenticationForm,
    PasswordResetForm, SetPasswordForm
)

from core.serializers import UserSerializer, UserRegistrationSerializer


class UserCreationView(FormView):
    form_class = UserCreationForm
    login = False

    def form_valid(self, form):
        form.save()
        if self.login:
            auth_form = AuthenticationForm(request=self.request, data={
                'username': form.cleaned_data['email'],
                'password': form.cleaned_data['password1']
            })
            if not auth_form.is_valid():
                raise Exception()
            else:
                auth_login(self.request, auth_form.user_cache)
        return super(UserCreationView, self).form_valid(form)


class TempFileUploadView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        """
        Method for saving temporary files
        ---
        # YAML (must be separated by `---`)

        parameters_strategy: merge

        parameters:
            - name: file
              type: file

        responseMessages:
            - code: 401
              message: Not authenticated

        consumes:
            - application/json
            - application/xml
        produces:
            - application/json
            - application/xml
        """
        file = request.FILES['file']

        import pdb; pdb.set_trace()
        return Response(dict(
            count=1,
            results=[
                dict(
                    name=file.get_file_url(),
                    url=os.path.join(settings.TEMP_FILES_URL, file.get_file_url())
                )
            ]
        ))


class UserApiView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    allowed_methods = ("GET", "POST", )
    queryset = get_user_model().objects.filter(is_active=True)
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        return super(UserApiView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Your docs
        ---
        # YAML (must be separated by `---`)

        serializer: core.serializers.UserSerializer
        omit_serializer: false

        parameters_strategy: merge

        parameters:
            - name: userpic
              type: file

        responseMessages:
            - code: 401
              message: Not authenticated

        consumes:
            - application/json
            - application/xml
        produces:
            - application/json
            - application/xml
        """
        return super(UserApiView, self).patch(request, *args, **kwargs)

    def get_object(self):
        return self.request.user


class RegistrationApiView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        """
        Your docs
        ---
        serializer: core.serializers.UserRegistrationSerializer
        omit_serializer: false

        parameters_strategy: merge

        parameters:
            - name: userpic
              type: file

        responseMessages:
            - code: 401
              message: Not authenticated

        consumes:
            - application/json
            - application/xml
        produces:
            - application/json
            - application/xml
        """
        return super(RegistrationApiView, self).post(request, *args, **kwargs)

    def perform_create(self, serializer):
        d = 3
        serializer.save()

    def get_object(self):
        return self.request.user


class AuthenticationView(FormView):
    form_class = AuthenticationForm

    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        return super(AuthenticationView, self).form_valid(form)


class EmailConfirmView(TemplateView):
    template_name = "profiles/email-confirmed.html"

    def get(self, request, uidb64=None, token=None, *args, **kwargs):
        UserModel = get_user_model()
        assert uidb64 is not None and token is not None  # checked by URLconf
        try:
            # urlsafe_base64_decode() decodes to bytestring on Python 3
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None
        if user is not None and default_token_generator.check_token(user, token):
            user.is_email_confirmed = True
            user.save()
            return super(EmailConfirmView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse_lazy("email-confirm-fail"))


class EmailConfirmFailView(TemplateView):
    template_name = "profiles/email-confirm-fail.html"


class SetPasswordView(FormView):
    template_name = "profiles/email-confirmed.html"
    form_class = SetPasswordForm

    def get_user_by_token(self, token, uidb64):
        UserModel = get_user_model()
        assert uidb64 is not None and token is not None  # checked by URLconf
        try:
            # urlsafe_base64_decode() decodes to bytestring on Python 3
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None
        if user is not None and default_token_generator.check_token(user, token):
            self.user_cache = user
            return user
        else:
            return None

    def get(self, request, uidb64=None, token=None, *args, **kwargs):
        user = self.get_user_by_token(token, uidb64)
        if user is None:
            raise Http404
        return super(SetPasswordView, self).get(request, *args, **kwargs)

    def post(self, request, uidb64=None, token=None, *args, **kwargs):
        user = self.get_user_by_token(token, uidb64)
        if user is None:
            raise Http404
        return super(SetPasswordView, self).post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(SetPasswordView, self).get_form_kwargs()
        kwargs['user'] = self.user_cache
        return kwargs

    def form_valid(self, form):
        form.save()
        return super(SetPasswordView, self).form_valid(form)


class SetNewPasswordView(FormView):
    template_name = "profiles/email-confirmed.html"
    form_class = SetNewPasswordForm

    def get_form_kwargs(self):
        kwargs = super(SetNewPasswordView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        form.save()
        form.user_cache.backend = 'django.contrib.auth.backends.ModelBackend'
        auth_login(self.request, form.user_cache)
        if self.request.is_ajax():
            return JsonResponse(data={'error': False})
        return super(SetNewPasswordView, self).form_valid(form)

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse(data=form.errors, status=400)
        return super(SetNewPasswordView, self).form_valid(form)


class PasswordResetEmailFormView(FormView):
    template_name = "profiles/email-confirmed.html"
    form_class = PasswordResetForm

    def form_valid(self, form):
        form.save()
        return super(PasswordResetEmailFormView, self).form_valid(form)


class LogOutView(RedirectView):

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super(LogOutView, self).get(request, *args, **kwargs)


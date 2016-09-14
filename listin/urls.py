"""listin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from django.conf.urls.i18n import i18n_patterns

from core.views import visitor
from core.views import user
from core.views import api

# profile related routing
from core.views.profile import(
    UserCreationView, AuthenticationView, LogOutView, EmailConfirmView,
    PasswordResetEmailFormView, SetPasswordView, EmailConfirmFailView,
    SetNewPasswordView, RegistrationApiView, UserApiView
)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^market/', include('market.urls')),
    url(r'^tracer/', include('tracer.urls')),

    # visitor views urls
    url(r'^$', visitor.HomePageView.as_view(), name='homepage'),
    url(r'^twillio/$', visitor.TwillioView.as_view(), name='twillio'),
    url(r'^organization/(?P<slug>[a-zA-Z0-9_\-]+)/$', visitor.OrganizationViewPage.as_view(), name="organization-view"),
    url(r'^organization/(?P<slug>[a-zA-Z0-9_\-]+)/vacanacies/$', visitor.OrganizationVacanciesPage.as_view(),
        name="organization-vacancies"),

    url(r'^organization/add/$', user.OrganizationView.as_view(), name='organization-add'),
    url(r'^organizations/(?P<pk>[0-9]+)/branches/add/$', user.BranchView.as_view(),
        name="branch-add"),
    url(r'^organizations/(?P<organization_pk>[0-9]+)/branches/(?P<pk>[0-9]+)/edit/$', user.BranchUpdateView.as_view(),
        name="branch-update"),

    # user (authorized) views
    url(r'^account/$', user.Account.as_view(), name='account'),
    url(r'^account/new/$', user.Account.as_view(is_new=True, business_needed=True), name='account-new'),
    url(r'^account/business/$', user.Account.as_view(business_needed=True), name='account-new-business'),

    # profile related urls
    url(r'^password/reset-done/$', user.ResetDone.as_view(), name='reset-done'),
    url(r'^password/new/$', SetNewPasswordView.as_view(), name='new-password'),

    url(r'^staff/add/$', user.StaffFormView.as_view(), name='staff-add'),
    url(r'^staff/(?P<pk>[0-9]+)/update/$', user.StaffUpdateView.as_view(), name="staff-update"),


    url(r'^vacancy/add/$', user.VacancyAddView.as_view(), name='vacancy-add'),
    url(r'^vacancy/(?P<pk>[0-9]+)/edit/$', user.VacancyUpdateView.as_view(), name="vacancy-edit"),


    url(r'^dashboard/$', user.Dashboard.as_view(), name='dashboard'),
    url(r'^files/temp/$', user.TempFilesView.as_view(), name='temp-files'),

    url(r'^messages/$', user.Messages.as_view(), name='messages'),
    url(r'^payment/$', user.PaymentView.as_view(), name='payment'),
    url(r'^tasks/add/$', user.TasksAdd.as_view(), name='tasks-add'),


    url(r'^products/add/$', user.ProductAddView.as_view(), name='product-add'),
    url(r'^products/(?P<pk>[0-9]+)/$', user.ProductDetailsView.as_view(), name='product-details'),
    url(r'^products/(?P<pk>[0-9]+)/update/$', user.ProductUpdate.as_view(), name='product-update'),

    url(r'^signup/success/$',
        UserCreationView.as_view(
            template_name="signup-success.html"
        ),
        name="signup-success"
        ),
    url(r'^signup/$',
        UserCreationView.as_view(
            template_name="signup.html",
            success_url=reverse_lazy('account-new'),
            login=True,
        ),
        name="signup",
        ),
    url(r'^login/$',
        AuthenticationView.as_view(
            template_name="login.html",
            success_url=reverse_lazy('account'),
        ),
        name="login"
        ),
    url(r'^logout/$',
        LogOutView.as_view(
            url=reverse_lazy('homepage'),
        ),
        name="logout"
        ),
    url(r'^email/password/reset/$',
        PasswordResetEmailFormView.as_view(template_name="password-reset.html",
                                           success_url=reverse_lazy("reset-confirm")), name='password-reset'),
    url(r'^email/password/reset/confirmed/$', user.ResetConfirmed.as_view(), name='reset-confirm'),
    url(r'^email/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        EmailConfirmView.as_view(template_name="email-confirm.html"), name='email-confirm'),
    url(r'^email/confirm/fail/$',
        EmailConfirmFailView.as_view(template_name="email-confirm-fail.html"), name='email-confirm-fail'),
    url(r'^email/password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        SetPasswordView.as_view(template_name="password-new.html", success_url=reverse_lazy("reset-done")),
        name='email-password-new'),
    # url(r'^social/auth/success/$', visitor.SocialAuthSuccess.as_view(success_url=reverse_lazy("reset-done")),
    #     name='social-auth-success'),
]

urlpatterns += i18n_patterns(*urlpatterns)
urlpatterns += url('', include('social.apps.django_app.urls', namespace='social')),

urlpatterns += [
    url(r'^api/', include([
        url(r'^', include('rest_framework_swagger.urls')),

        url(r'^auth/login/$', RegistrationApiView.as_view(), name="api-login"),
        url(r'^auth/signup/$', RegistrationApiView.as_view(), name="api-signup"),

        url(r'^branches/$', api.BranchesList.as_view(), name="api-branches"),


        url(r'^profile/$', UserApiView.as_view(), name="api-profile"),

        url(r'^categories/$', api.CategoriesApiView.as_view(), name="api-categories"),

        url(r'^files/temp/$', api.TempFileApiView.as_view(),
            name="api-tempfile"),

        url(r'^organizations/my/$', api.BusinessDetails.as_view(),
            name="api-organization"),
        url(r'^organizations/$', api.BusinessListView.as_view(),
            name="api-organizations-list"),
        url(r'^organizations/(?P<organization_pk>[0-9]+)/visitor-message/$', api.VisitorMessageApiView.as_view(),
            name="api-visitor-message"),
        url(r'^organizations/(?P<organization_pk>[0-9]+)/staff/$', api.BusinessStaffList.as_view(),
            name="api-staff-list"),
        url(r'^rating/$', api.RatingList.as_view(), name="api-rating"),
        url(r'^organizations/(?P<organization_pk>[0-9]+)/messages/$', api.OrganizationMessagesListView.as_view(),
            name="api-messages-list"),
        url(r'^partners/$', api.OrganizationPartnersListView.as_view(),  name="api-partners-list"),
        url(r'^organizations/favorites/$', api.FavoriteBusinessList.as_view(),
            name="api-organizations-favorites"),

        url(r'^vacancies/$', api.VacanciesListView.as_view(), name="api-vacanacies-list"),
        url(r'^vacancies/(?P<pk>[0-9]+)/', api.VacanciesUpdateView.as_view(), name="api-vacancies-update"),

        url(r'^products/(?P<pk>[0-9]+)/$', api.ProductDetailsView.as_view(),
            name="api-product-details"),

        url(r'^products/$', api.ProductListView.as_view(),
            name="api-products-list"),

        url(r'^vacancies/(?P<pk>[0-9]+)/', api.VacanciesUpdateView.as_view(),
            name="api-vacancies-update"),

        url(r'^comments/$', api.CommentListCreate.as_view(is_own_company=False), name="api-comments"),
    ])),
]
if settings.DEBUG:
    urlpatterns += (
        url(r'^(media|cache)/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True} ),
        )

"""
Module that contains views for authorized users, which
usually have registered organization.
"""

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.http.response import HttpResponseRedirect
from django.utils.encoding import force_text
from django.views import generic
from django.utils.decorators import method_decorator

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse


from core.serializers import OrganizationProductSerializer
from core.decorators import company_required

from core import mailing
from core import models as business_models
from core.models import (
    Organization, OrganizationProduct,
    Staff, Category, Vacancy, Branch
)

from core.forms import (
    UserChangeForm, SetNewPasswordForm, OrganizationForm,
    ProductForm, StaffForm, VacancyForm, BranchForm
)
from jobs.forms import CVForm
from rest_framework.response import Response

from tasklist.forms import TaskForm
from tasklist.models import Task

from messaging.forms import MessageForm


@method_decorator(login_required(), 'dispatch')
class Account(generic.FormView):
    template_name = 'account.html'
    form_class = UserChangeForm
    success_url = reverse_lazy('account')
    is_new = False
    business_needed = False

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(Account, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        form.save()
        if self.request.is_ajax():
            return JsonResponse(data=dict(
                error=False,
            ))
        return super(Account, self).form_valid(form)

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        return super(Account, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(Account, self).get_context_data(**kwargs)
        try:
            organization = Organization.objects.get(user=self.request.user)
            context['organization_form'] = OrganizationForm(user=self.request.user,
                                                            instance=organization)
            context['staff'] = Staff.objects.filter(organization=organization)
            context['instance'] = organization
        except ObjectDoesNotExist:
            context['organization_form'] = OrganizationForm(user=self.request.user)
            context['instance'] = Organization()
        context['new_account'] = self.is_new
        context['cv_form'] = CVForm()
        context['new_password_form'] = SetNewPasswordForm(self.request)
        context['user'] = self.request.user
        context['business_needed'] = self.business_needed
        context['categories'] = Category.objects.get_tree()
        return context


class ResetConfirmed(generic.TemplateView):
    template_name = 'password-reset-confirm.html'


class ResetDone(generic.TemplateView):
    template_name = 'password-reset-done.html'


@method_decorator(company_required(business_add_url=reverse_lazy("account-new-business")), 'dispatch')
class Dashboard(generic.TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(Dashboard, self).get_context_data(**kwargs)
        business = Organization.objects.filter(user=self.request.user).first()
        context['organization'] = business
        context['staff'] = business_models.Staff.objects.filter(organization=business)
        context['tasks'] = Task.objects.filter(added_by=self.request.user)
        return context


@method_decorator(company_required(business_add_url=reverse_lazy("account-new-business")), 'dispatch')
class VacancyAddView(generic.FormView):
    template_name = 'vacancy-add.html'
    form_class = VacancyForm
    success_url = reverse_lazy("company")

    def get_form_kwargs(self):
        kwargs = super(VacancyAddView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_invalid(self, form):
        raise NotImplementedError("Invalid form %s" % form.errors.as_text())

    def get_context_data(self, **kwargs):
        context = super(VacancyAddView, self).get_context_data(**kwargs)
        context['organization'] = Organization.objects.get_company(self.request.user)
        context['vacancy'] = None
        context['degree_choices'] = Vacancy.degree_choices()
        return context

    def form_valid(self, form):
        organization = Organization.objects.filter(user=self.request.user).first()
        form.save(organization)
        if self.request.is_ajax():
            return JsonResponse(data={
                'error': False
            })
        return super(VacancyAddView, self).form_valid(form)


@method_decorator(company_required(business_add_url=reverse_lazy("account-new-business")), 'dispatch')
class VacancyUpdateView(generic.DetailView):
    template_name = 'vacancy-add.html'
    queryset = Vacancy.objects.all()

    def get_context_data(self, **kwargs):
        context = super(VacancyUpdateView, self).get_context_data(**kwargs)
        obj = self.get_object()
        context['organization'] = Organization.objects.get_company(self.request.user)
        context['degree_choices'] = obj.degree_choices()
        return context


@method_decorator(company_required(business_add_url=reverse_lazy("account-new-business")), 'dispatch')
class TempFilesView(generic.TemplateView):
    template_name = 'dashboard.html'

    def post(self, request, *args, **kwargs):
        file = request.FILES['file']
        return JsonResponse(dict(result='ok', file_path=file.file.name))

    def get_context_data(self, **kwargs):
        context = super(TempFilesView, self).get_context_data(**kwargs)
        return context


@method_decorator(company_required(business_add_url=reverse_lazy("account-new-business")), 'dispatch')
class Messages(generic.FormView):
    template_name = 'dashboard.html'
    form_class = MessageForm
    success_url = '/dash'

    def get_form_kwargs(self):
        kwargs = super(Messages, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        room = form.save()
        if self.request.is_ajax():
            return JsonResponse(data=dict(
                result="Ok",
                error=False,
                room_id=room.pk,
            ))
        return super(Messages, self).form_valid(form)


@method_decorator(company_required(business_add_url=reverse_lazy("account-new-business")), 'dispatch')
class PaymentView(generic.TemplateView):
    template_name = 'payment.html'
    success_url = '/dash'


@method_decorator(company_required(business_add_url=reverse_lazy("account-new-business")), 'dispatch')
class TasksAdd(generic.FormView):
    template_name = 'tasks-add.html'
    form_class = TaskForm
    success_url = reverse_lazy('tasks-dashboard')

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(TasksAdd, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(TasksAdd, self).get_context_data(**kwargs)
        business = Organization.objects.filter(user=self.request.user).first()
        context['business'] = business
        context['staff'] = business_models.Staff.objects.filter(business=business)
        context['PRIORITY_CHOICES'] = Task.PRIORITY_CHOICES
        context['STATUS_CHOICES'] = Task.STATUS_CHOICES
        context['ASSIGN_CHOICES'] = Staff.objects.filter(business=business)
        return context

    def form_valid(self, form):
        form.save()
        return super(TasksAdd, self).form_valid(form)


@method_decorator(company_required(business_add_url=reverse_lazy("account-new-business")), 'dispatch')
class StaffFormView(generic.FormView):
    template_name = 'staff.html'
    form_class = StaffForm

    def get_success_url(self, organization):
        """
        Returns the supplied success URL.
        """
        # Forcing possible reverse_lazy evaluation
        return force_text(reverse_lazy('organization-view', kwargs={
            'slug': organization.slug
        }))

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(StaffFormView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        instance = form.save()
        mailing.send_staff_invitation(instance)
        if self.request.is_ajax():
            return JsonResponse(data=dict(
                error=False,
            ))
        return HttpResponseRedirect(self.get_success_url(instance.organization))

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        return super(StaffFormView, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(StaffFormView, self).get_context_data(**kwargs)
        try:
            context['business_form'] = OrganizationForm(user=self.request.user,
                                                        instance=Organization.objects.all().first())
        except ObjectDoesNotExist:
            pass
        return context


class StaffUpdateView(generic.UpdateView):
    template_name = 'staff.html'
    form_class = StaffForm
    success_url = reverse_lazy('company')
    queryset = Staff.objects.all()

    def get_context_data(self, **kwargs):
        context = super(StaffUpdateView, self).get_context_data(**kwargs)
        try:
            context['business_form'] = OrganizationForm(user=self.request.user,
                                                        instance=Organization.objects.all().first())
        except ObjectDoesNotExist:
            pass
        return context

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(StaffUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super(StaffUpdateView, self).form_valid(form)

    def get_queryset(self):
        return super(StaffUpdateView, self).get_queryset().filter(user=self.request.user)


class OrganizationView(generic.FormView):
    template_name = 'account.html'
    form_class = OrganizationForm
    success_url = reverse_lazy("companies")

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(OrganizationView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        try:
            business = Organization.objects.get(user=self.request.user, branch__isnull=True)
        except ObjectDoesNotExist:
            pass
        else:
            kwargs['instance'] = business
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(OrganizationView, self).get_context_data(**kwargs)
        context['companies'] = Organization.objects.filter(user=self.request.user)
        return context

    def form_valid(self, form):
        form.save()
        if self.request.is_ajax():
            return JsonResponse(dict(result="OK"), status=200)
        return super(OrganizationView, self).form_valid(form)

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        return super(OrganizationView, self).form_valid(form)


class BranchView(generic.FormView):
    template_name = 'branch.html'
    form_class = BranchForm
    success_url = reverse_lazy("company")

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(BranchView, self).get_form_kwargs()
        kwargs['user'] = self.request.user

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(BranchView, self).get_context_data(**kwargs)
        context['companies'] = Organization.objects.filter(user=self.request.user)
        try:
            organization = Organization.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            pass
        else:
            context['organization'] = organization
        return context

    def form_valid(self, form):
        form.save()
        if self.request.is_ajax():
            return JsonResponse(dict(result="OK"), status=200)
        return super(BranchView, self).form_valid(form)

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        return super(BranchView, self).form_invalid(form)


class BranchUpdateView(generic.UpdateView):
    template_name = 'branch.html'
    form_class = BranchForm
    success_url = reverse_lazy("company")
    queryset = Branch.objects.all()

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(BranchUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(BranchUpdateView, self).get_context_data(**kwargs)
        context['companies'] = Organization.objects.filter(user=self.request.user)
        try:
            organization = Organization.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            pass
        else:
            context['organization'] = organization
        return context

    def form_valid(self, form):
        form.save()
        if self.request.is_ajax():
            return JsonResponse(dict(result="OK"), status=200)
        return super(BranchUpdateView, self).form_valid(form)

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        return super(BranchUpdateView, self).form_invalid(form)


class ProductDetailsView(generic.DetailView):
    template_name = 'product-details.html'
    queryset = OrganizationProduct.objects.all()


class ProductAddView(generic.FormView):
    template_name = 'product-form.html'
    form_class = OrganizationProductSerializer
    success_url = reverse_lazy("company")

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = {}
        if self.request.method in ('POST', 'PUT'):
            data = self.request.POST
            data.update(self.request.FILES)
            kwargs.update({
                'context': {
                    'user': self.request.user
                },
                'data': data
            })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ProductAddView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.get_tree()
        context['organization'] = self.request.user.organization_set.first()
        return context

    def form_invalid(self, form):
        if self.request.is_ajax():
            return Response(form.errors)

    def form_valid(self, form):
        form.save()
        if self.request.is_ajax():
            pass

        return super(ProductAddView, self).form_valid(form)


class ProductUpdate(generic.UpdateView):
    template_name = 'product-form.html'
    form_class = ProductForm
    success_url = reverse_lazy("company")
    queryset = business_models.Product.objects.all()

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(ProductUpdate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ProductUpdate, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.get_tree()
        context['instance'] = OrganizationProduct.objects.get(product=self.object)
        context['organization'] = context['instance'].organization
        return context

    def form_valid(self, form):
        form.save()
        return super(ProductUpdate, self).form_valid(form)

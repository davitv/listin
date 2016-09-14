from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model

import django_filters

from rest_framework import generics
from rest_framework import status
from rest_framework import filters
from rest_framework import exceptions
from rest_framework import mixins
from rest_framework.response import Response

from core.serializers import (
    OrganizationSerializer, BranchSerializer, CommentSerializer, StaffSerializer,
    RatingResponseSerializer, VacancySerializer, TempFileUploadSerializer,
    VisitorMessageSerializer, OrganizationProductSerializer, CategorySerializer,
)

from core.models import (
    Organization, Branch, Comment, Staff,
    Rating, Vacancy, Partnership,
    Category, VisitorMessage
)

from market.models import Product

from messaging.models import Message, Room
from messaging.serializers import MessageSerializer


class BusinessDetails(mixins.UpdateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin,
                      generics.GenericAPIView):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super(BusinessDetails, self).get_serializer_context()
        context.update({'user': self.request.user})
        return context

    def post(self, request, *args, **kwargs):
        try:
            # This query needed only for figuring out whether
            # organization already exists.
            # TODO: find another workaround
            Organization.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            return self.create(request, *args, **kwargs)
        return self.partial_update(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Returns info about authorized user's organization.
        """
        return super(BusinessDetails, self).retrieve(request, *args, **kwargs)

    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        try:
            obj = Organization.objects.get(user=self.request.user)
        except ObjectDoesNotExist:
            raise generics.Http404

        return obj


class BusinessListView(generics.ListAPIView):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend)
    filter_fields = ('category', 'country', )
    search_fields = ('name', 'description', )


class VisitorMessageApiView(generics.ListCreateAPIView):
    serializer_class = VisitorMessageSerializer
    queryset = VisitorMessage.objects.all()
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend)

    def get_queryset(self):
        queryset = super(VisitorMessageApiView, self).get_queryset()
        return queryset.filter(organization__pk=self.kwargs.get('organization_pk', 0))

    def get_serializer_context(self):
        context = super(VisitorMessageApiView, self).get_serializer_context()
        if self.request.user.is_authenticated:
            context['user'] = self.request.user
        try:
            context['organization'] = self.kwargs.get('organization_pk', 0)
        except ObjectDoesNotExist:
            pass
        return context


class CategoriesApiView(generics.GenericAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get(self, request, *args, **kwargs):
        ret = Category.objects.get_serialized_tree(self.serializer_class)
        return Response(data=dict(
            results=ret
        ))


class FavoriteBusinessList(generics.ListAPIView):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()

    def get_queryset(self):
        queryset = super(FavoriteBusinessList, self).get_queryset()
        pks = self.request.query_params.get('pks', None)
        try:
            pks = [int(x) for x in pks.split(',')]
        except ValueError:
            raise generics.Http404
        except AttributeError:
            raise generics.Http404
        else:
            queryset = queryset.filter(pk__in=pks)
        return queryset


class BranchesList(generics.ListAPIView):
    serializer_class = BranchSerializer
    queryset = Branch.objects.all()


class CommentListCreate(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    filter_fields = ('organization', )
    is_own_company = False

    def get_serializer_context(self):
        context = super(CommentListCreate, self).get_serializer_context()
        context['user'] = self.request.user
        return context

    def get(self, request, *args, **kwargs):
        """
        ---
        response_serializer: CommentSerializer
        parameters:
            - name: organization
              type: int
              paramType: query
        """
        try:
            assert self.request.GET.get('organization', False)
        except AssertionError:
            raise generics.Http404
        return super(CommentListCreate, self).get(request, *args, **kwargs)


class BusinessStaffList(generics.ListAPIView):
    serializer_class = StaffSerializer
    queryset = Staff.objects.all()
    filter_fields = ('organization', )

    def get_queryset(self):
        """
        Filter queryset by organization_pk from url
        regex pattern.
        """
        queryset = super(BusinessStaffList, self).get_queryset()
        try:
            organization_pk = self.kwargs['organization_pk']
        except KeyError:
            raise generics.Http404
        else:
            queryset = queryset.filter(organization=organization_pk)

        return queryset


class OrganizationMessagesFilter(filters.FilterSet):
    recipients = django_filters.MethodFilter(action='find_room')

    def find_room(self, queryset, value):
        try:
            pks = [int(num) for num in value.split(',')]
            pks.append(self.request.user.pk)
        except ValueError:
            raise generics.Http404
        else:
            room = Room.objects.get_or_create_room(get_user_model().objects.filter(pk__in=pks))
        return queryset.filter(room=room)

    class Meta:
        model = Message
        fields = ['recipients', ]


class OrganizationMessagesListView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    queryset = Message.objects.all().select_related('message')

    def get_queryset(self):
        queryset = super(OrganizationMessagesListView, self).get_queryset()
        queryset = queryset.filter(user=self.request.user)
        # not using OrganizationMessagesFilter because can't get
        # request object there
        # TODO: dig docs for making it available
        if self.request.GET.get('recipients', False):
            try:
                pks = [int(num) for num in self.request.GET.get('recipients').split(',')]
                pks.append(self.request.user.pk)
            except ValueError:
                raise generics.Http404
            else:
                room = Room.objects.get_or_create_room(get_user_model().objects.filter(pk__in=pks))
                queryset.filter(room=room)
        else:
            organization_pk = self.kwargs.get('organization_pk')
            organization = Organization.objects.get(pk=organization_pk)
            queryset.filter(room=organization.get_messaging_room())

        return queryset

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super(OrganizationMessagesListView, self).get_serializer_context()
        context['user'] = self.request.user
        organization_pk = self.kwargs.get('organization_pk')
        organization = Organization.objects.get(pk=organization_pk)
        context['room'] = organization.get_messaging_room()
        return context

    def create(self, request, organization_pk=None, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        headers = self.get_success_headers(self.serializer_class(instance=comment).data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class OrganizationPartnersListView(generics.ListCreateAPIView):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()

    def get_queryset(self):
        queryset = super(OrganizationPartnersListView, self).get_queryset()
        print(">>>>" * 10)
        organization_id = self.request.GET.get('organization_id', 0)
        organization = Organization.objects.get(pk=organization_id)

        sent_requests = Partnership.objects.filter(status=1, organization=organization)\
            .select_related('partner')

        received_requests = Partnership.objects.filter(status=1, partner=organization)\
            .select_related('organization')

        # Collect pks and filter again
        queryset = queryset.filter(
            pk__in=[partnership.partner.pk for partnership in sent_requests] +
                   [partnership.organization.pk for partnership in received_requests]
        )
        return queryset

    def create(self, request, organization_pk=None, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        headers = self.get_success_headers(self.serializer_class(instance=comment).data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class VacanciesListView(generics.ListCreateAPIView):
    serializer_class = VacancySerializer
    queryset = Vacancy.objects.all().select_related('cv')

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super(VacanciesListView, self).get_serializer_context()
        context.update({'user': self.request.user})
        return context


class ProductListView(mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      generics.GenericAPIView):
    serializer_class = OrganizationProductSerializer
    queryset = Product.objects.all()

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super(ProductListView, self).get_serializer_context()
        context.update({'user': self.request.user})
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get('pk', False):
            self.kwargs['pk'] = request.POST.get('pk')
            return self.partial_update(request, *args, **kwargs)
        return self.create(request, *args, **kwargs)


class ProductDetailsView(generics.RetrieveAPIView):
    serializer_class = OrganizationProductSerializer
    queryset = Product.objects.all()

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super(ProductDetailsView, self).get_serializer_context()
        context.update({'user': self.request.user})
        return context


class VacanciesUpdateView(mixins.UpdateModelMixin,
                          generics.RetrieveAPIView):
    serializer_class = VacancySerializer
    queryset = Vacancy.objects.all().select_related('cv')

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super(VacanciesUpdateView, self).get_serializer_context()
        context.update({'user': self.request.user})
        return context

    def post(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class RatingList(mixins.RetrieveModelMixin,
                 mixins.CreateModelMixin,
                 generics.GenericAPIView):
    serializer_class = RatingResponseSerializer
    queryset = Rating.objects.all()
    filter_fields = ('organization', )

    def retrieve(self, request, *args, **kwargs):
        organization_id = request.GET.get('organization_id', 0)
        queryset = Rating.objects.filter(organization__pk=organization_id)
        total = queryset.count()
        positive = queryset.filter(is_positive=True).count()
        negative = queryset.filter(is_positive=False).count()

        return Response(data={
            'total': total,
            'positive': positive,
            'negative': negative,
        })

    def create(self, request, *args, **kwargs):
        data = dict(
            user=request.user.pk,
            organization=kwargs['pk'],
            is_positive=request.POST.get('is_positive')
        )
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        You should be authorized to use this method.
        ---

        parameters_strategy: replace
        parameters:
        - name: pk
          description: organization idetificator in path
          required: true
          type: int
          paramType: path
        - name: is_positive
          description: 1 if positive, 0 otherwise
          required: true
          type: int
          paramType: form

        """
        if not request.user.is_authenticated():
            raise exceptions.NotAuthenticated
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class TempFileApiView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        file = request.FILES['file']
        serializer = TempFileUploadSerializer(data={
            'file': file
        })
        if serializer.is_valid():
            instance = serializer.save()
            return Response(data={
                'count': 1,
                'results': [
                    instance
                ]
            })
        return Response(data=serializer.errors)

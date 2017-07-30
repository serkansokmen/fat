import requests
import json
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Count, Q
from django.views.generic.base import TemplateView
from django.utils.translation import ugettext_lazy as _
from django.http import JsonResponse
from django_filters import rest_framework as filters
from rest_framework import viewsets, parsers, views, mixins, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import list_route, detail_route
from rest_framework import status
from .models import Search, Image, DiscardedImage, Annotation, SemanticCheck, \
    AnnotationSemanticCheck, MarkedObject
from .serializers import SearchSerializer, ImageSerializer, AnnotationSerializer, \
    SemanticCheckSerializer, AnnotationSemanticCheckSerializer, MarkedObjectSerializer



class HomeView(TemplateView):
    template_name = 'flickr/app.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['static_hosting_url'] = settings.STATIC_HOSTING_URL
        return context


def make_search_query(request, flickr_page=0):

    req_data = request.GET if request.method == 'GET' else request.data
    req_page = int(req_data.get('page', '1'))
    req_perpage = int(req_data.get('perpage', '10'))

    tags = req_data.get('tags', None)
    tag_mode = req_data.get('tag_mode')
    licenses = req_data.get('licenses')
    user_id = req_data.get('user_id')

    flickr_perpage =  req_data.get('flickr_perpage', 500)

    if tags is None:
        return Response({
            'message': _('`tags` field is required to make a query.')
        })

    tags = tags.replace(' ', '')
    req = requests.get('https://api.flickr.com/services/rest/?method=flickr.photos.search',
        params={
            'api_key': settings.FLICKR_API_KEY,
            'api_secret': settings.FLICKR_API_SECRET,
            'format': 'json',
            'nojsoncallback': 1,
            'license': licenses,
            'safe_search': 3,
            'sort' : 'relevance',
            'media': 'photos',
            'content_type': 7,
            'extras': 'license,tags',
            'per_page': flickr_perpage,
            'page': str(flickr_page),
            'tags': tags,
            'tag_mode': tag_mode})
    if req.json()['stat'] == 'ok':
        return req.json()
    return None


def get_filtered_images(photos, cursor, perpage):
    filtered_images = []
    for image in photos:
        existing_in_search = Image.objects.filter(id=image.get('id')).count()
        existing_discarded = DiscardedImage.objects.filter(id=image.get('id')).count()
        if existing_in_search + existing_discarded == 0:
            filtered_images.append(image)
    return filtered_images[cursor:cursor + perpage]


@api_view(['GET', 'POST', 'PUT'])
def flickr(request):

    req_data = request.GET if request.method == 'GET' else request.data

    req_page = int(req_data.get('page', '1'))
    req_perpage = int(req_data.get('perpage', '10'))
    req_cursor = req_perpage * (req_page - 1)

    tags = req_data.get('tags', None)
    tag_mode = req_data.get('tag_mode')
    licenses = req_data.get('licenses')
    user_id = req_data.get('user_id')

    if request.method == 'GET':

        (search, created) = Search.objects.get_or_create(
            tags=tags,
            defaults={
                'tag_mode': tag_mode,
                'licenses': licenses,
                'user_id': user_id,
            }
        )
        json = make_search_query(request)

        if json is None:
            return Response({'message': _('An error occured parsing response data.')})

        results = json['photos']
        flickr_pages = int(results['pages'])
        flickr_page = int(results['page'])
        flickr_total = int(results['total'])
        photos_results = results['photo']

        search_serializer = SearchSerializer(search)
        image_serializer = ImageSerializer(data=photos_results, many=True)

        if flickr_total == search.images.all() or flickr_total == 0:

            # check if all is already added
            return Response({
                'total': 0,
                'search': search_serializer.data,
                'images': [],
                'page': req_page,
                'perpage': req_perpage,
            }, status=status.HTTP_404_NOT_FOUND)

        else:

            filtered_images = get_filtered_images(photos_results, req_cursor, req_perpage)
            photos_result_ids = [p.get('id') for p in photos_results]

            if len(photos_results) > 0:

                already_selected_count = search.images.filter(id__in=photos_result_ids).count()

                return Response({
                    'total': flickr_total,
                    'left': max(flickr_total - already_selected_count - search.images.count(), 0),
                    'search': search_serializer.data,
                    'images': filtered_images,
                    'page': req_page,
                    'perpage': req_perpage,
                    'cursor': (req_page - 1) * req_perpage,
                })
            else:
                if flickr_page < flickr_pages:

                    json = make_search_query(request, flickr_page=flickr_page + 1)

                    if json is None:
                        return Response({'message': _('An error occured parsing response data.')})
                    results = json['photos']
                    flickr_pages = int(results['pages'])
                    flickr_page = int(results['page'])
                    flickr_total = int(results['total'])
                    photos_results = results['photo']
                    return Response({
                        'total': flickr_total,
                        'left': max(flickr_total - search.images.count(), 0),
                        'search': search_serializer.data,
                        'images': [],
                        'page': req_page,
                        'perpage': req_perpage,
                        'cursor': (req_page - 1) * req_perpage,
                    })
                else:
                    return Response({
                        'total': flickr_total,
                        'left': 0,
                        'search': search_serializer.data,
                        'images': [],
                        'page': req_page,
                        'perpage': req_perpage,
                    }, status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'POST' or request.method == 'PUT':

        images_data = request.data.get('images', None)
        if images_data is None:
            return Response({'message': _('Some images are required')})

        (search, created) = Search.objects.get_or_create(
            tags=request.data.get('tags'), defaults=request.data)
        search_serializer = SearchSerializer(search)
        image_serializer = ImageSerializer(data=images_data, many=True)

        if image_serializer.is_valid():
            for image in image_serializer.validated_data:
                state = image.pop('state')
                if state == 0:
                    (selected, created) = Image.objects.get_or_create(id=image.get('id'), defaults=image)
                    if selected not in search.images.all():
                        search.images.add(selected)
                elif state == 1:
                    (discarded, created) = DiscardedImage.objects.get_or_create(id=image.get('id'), defaults=image)
            search.save()

        json = make_search_query(request)

        if json is None:
            return Response({'message': _('An error occured parsing response data.')})

        results = json['photos']
        flickr_pages = int(results['pages'])
        flickr_page = int(results['page'])
        flickr_total = int(results['total'])
        filtered_images = get_filtered_images(results['photo'], req_cursor, req_perpage)

        return Response({
            'total': flickr_total,
            'left': max(flickr_total - search.images.count(), 0),
            'search': search_serializer.data,
            'images': filtered_images,
            'page': req_page,
            'perpage': req_perpage,
            'cursor': (req_page - 1) * req_perpage,
        })

    return Response({'message': _('GET, POST or PUT required.')}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 10000


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class SearchQueryView(views.APIView):

    def post(self, request, format=None):
        serializer = SearchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors)


class SearchViewSet(viewsets.ModelViewSet):

    serializer_class = SearchSerializer
    queryset = Search.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('tags',)
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        queryset = Search.objects.all()
        query = self.request.query_params.get('q', None)
        if query is not None:
            queryset = queryset.filter(tags__icontains=query)
        return queryset



class ImageViewSet(viewsets.ModelViewSet):

    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        if 'annotated_only' in self.request.query_params:
            return Image.objects.filter(Q(annotation__exact=None) or Q(annotation__is_approved=False))
        return Image.objects.all()


class AnnotationViewSet(viewsets.ModelViewSet):

    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer
    pagination_class = StandardResultsSetPagination

    def retrieve(self, request, pk=None):
        annotation = get_object_or_404(self.queryset, pk=pk)
        serializer = self.get_serializer(annotation)
        return Response(serializer.data)

    # def create(self, request):
    #     image_id = get_object_or_404(Image, pk=request.data.get('image'))
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.image_id = image_id
    #     if serializer.is_valid():
    #         serializer.save()
    #         # annotation = Annotation.objects.create(**serializer.data)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors)

    def partial_update(self, request, pk=None):
        if pk is not None:
            annotation = Annotation.objects.get(pk=pk)

            semantic_checks = request.data.get('semantic_checks')
            if semantic_checks is not None:
                AnnotationSemanticCheck.objects.filter(annotation=annotation).delete()
                annotation_semantic_check_serializer = AnnotationSemanticCheckSerializer(
                    data=semantic_checks, many=True)
                if annotation_semantic_check_serializer.is_valid():
                    annotation_semantic_check_serializer.save()

            marked_objects = request.data.get('marked_objects')
            if marked_objects is not None:
                # marked_objects_serializer = MarkedObjectSerializer(data=marked_objects, many=True)
                annotation.marked_objects.all().delete()
                for data in marked_objects:
                    marked_object = MarkedObject.objects.create(**data)
                    # import ipdb; ipdb.set_trace()
                    annotation.marked_objects.add(marked_object)
                annotation.save()
            annotation_serializer = self.get_serializer(annotation)
            return Response(annotation_serializer.data)


class SemanticCheckViewSet(viewsets.ModelViewSet):

    queryset = SemanticCheck.objects.all()
    serializer_class = SemanticCheckSerializer
    pagination_class = StandardResultsSetPagination


class AnnotationSemanticCheckViewSet(viewsets.ModelViewSet):

    queryset = AnnotationSemanticCheck.objects.all()
    serializer_class = AnnotationSemanticCheckSerializer
    pagination_class = StandardResultsSetPagination

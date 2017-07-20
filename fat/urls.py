from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework import routers
from rest_framework.schemas import get_schema_view
import flickr.api as flickr_api
from flickr.api import flickr

schema_view = get_schema_view(title='Flickr Search Tool API')

router = routers.DefaultRouter()
router.register(r'search', flickr_api.SearchViewSet)
router.register(r'images', flickr_api.ImageViewSet)
router.register(r'annotations', flickr_api.AnnotationViewSet)
# router.register(r'licenses', flickr_api.LicenseViewSet)

urlpatterns = [
    url(r'^api/v1/', include(router.urls)),
]

urlpatterns += [
    url(r'^admin/', admin.site.urls),
    url(r'^auth/', include('rest_auth.urls')),
    url(r'^api/v1/licenses/', flickr_api.LicenseView.as_view()),
    url(r'^api/v1/schema/$', schema_view),
    url(r'^api/v1/flickr/', flickr, name='flickr'),
    url(r'^$', TemplateView.as_view(template_name='flickr/app.html')),
    url(r'^flickr/', include('flickr.urls')),
]

if settings.DEBUG == True:
    urlpatterns += static(settings.STATIC_URL,
        document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT)

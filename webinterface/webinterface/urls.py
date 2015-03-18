from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static
import os
print os.getcwd()
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'webinterface.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', 'webinterface.views.home'),
    url(r'^admin/', include(admin.site.urls)),
) + static('test_frames/', document_root=os.path.join(os.getcwd(), 'test_videos/frames/'))

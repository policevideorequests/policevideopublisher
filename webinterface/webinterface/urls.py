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
    url(r'^test_ffmpeg_options/$', 'webinterface.views.test_ffmpeg_options'),
    url(r'^current_settings/$', 'webinterface.views.current_settings'),
    url(r'^change_settings/$', 'webinterface.views.change_settings'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^is_logged_in/$', 'webinterface.views.is_logged_in'),
    url(r'^test_frames/(?P<filename>[\w\d_\.]+)$', 'webinterface.views.test_frames'),
    url(r'^login/$', 'webinterface.views.login'),
    url(r'^logout/$', 'webinterface.views.logout'),
    #url(r'^report/$', 'webinterface.views.report'),
    url(r'^mark_word_as_(?P<the_type>\w+)/$', 'webinterface.views.mark_word'),
    url(r'^email_report/$', 'webinterface.views.email_report'),
    url(r'^overredact_reports/$', 'webinterface.views.overredact_reports'),
) 
# + static('test_frames/', document_root=os.path.join(os.getcwd(), 'test_videos/frames/'))

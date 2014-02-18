from django.conf.urls.defaults import *


urlpatterns = patterns('',
    url(r'api/', include('piston.test_integration.testapp.urls'))
)

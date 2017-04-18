from django.conf.urls import url, include
from django.contrib import admin

import autofixture
autofixture.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('tests.testapp.urls'))
]

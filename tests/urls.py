from django.conf.urls import url
from django.contrib import admin

import autofixture
autofixture.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
]

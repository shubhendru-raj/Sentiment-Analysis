from django.conf.urls import patterns, url
from analyze.views import AnalyzeAPIView

urlpatterns = patterns(
    '',
    url(r'^analyze/$', AnalyzeAPIView.as_view(), name="analyze-api")
)

from django.urls import include, path
from rest_framework import routers
from . import views
from rest_framework.authtoken.views import obtain_auth_token

router = routers.DefaultRouter()
router.register(r'Assessment', views.AssessmentViewSet)
router.register(r'Question', views.QuestionViewSet)
router.register(r'Exhibit', views.ExhibitViewSet)
router.register(r'Role', views.RoleViewSet)
router.register(r'Excel', views.ExcelViewSet)
router.register(r'Cwf', views.CwfViewSet)
router.register(r'Kt', views.KtViewSet)
router.register(r'Stage', views.StageViewSet)
router.register(r'Qtype', views.QtypeViewSet)
router.register(r'Comment', views.CommentViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('api/', include(router.urls)),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
]

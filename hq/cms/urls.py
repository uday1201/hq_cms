from django.urls import include, path
from rest_framework import routers
from . import views
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.documentation import include_docs_urls
from django.conf import settings
from django.conf.urls.static import static


router = routers.DefaultRouter()
router.register(r'Assessment', views.AssessmentViewSet)
router.register(r'AssessmentProd', views.AssessmentProdViewSet)
router.register(r'QuestionProd', views.QuestionProdViewSet)
router.register(r'AssessmentFinal', views.AssessmentFinalViewSet)
router.register(r'QuestionFinal', views.QuestionFinalViewSet)
router.register(r'Question', views.QuestionViewSet)
router.register(r'Exhibit', views.ExhibitViewSet)
router.register(r'Role', views.RoleViewSet)
router.register(r'Excel', views.ExcelViewSet)
router.register(r'Cwf', views.CwfViewSet)
router.register(r'Kt', views.KtViewSet)
router.register(r'Stage', views.StageViewSet)
router.register(r'Qtype', views.QtypeViewSet)
router.register(r'Comment', views.CommentViewSet)
router.register(r'Users', views.UserViewSet)
router.register(r'snippet', views.SnippetViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('api/', include(router.urls)),
    #path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('docs/', include_docs_urls(title='Snippet API')),
    path('api/logout/', views.Logout.as_view(), name='Logout'),
    path('api/CwfKtStage/', views.CwfKtStage.as_view(), name='CwfKtStage'),
    path('api/CopyQuestion/', views.CopyQuestion.as_view(), name='CopyQuestion'),
    path('api/MoveToProd/', views.MoveToProd.as_view(), name='MoveToProd'),
    path('api/MigrateDBProd/', views.MigrateDBProd.as_view(), name='MigrateDBProd'),
    path('api/MoveToFinal/', views.MoveToFinal.as_view(), name='MoveToFinal'),
    path('api/login/', views.CustomObtainAuthToken.as_view(), name='CustomObtainAuthToken'),
    path('silk/', include('silk.urls', namespace='silk')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

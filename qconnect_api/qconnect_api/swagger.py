from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

def swagger_info():
    return openapi.Info(
        title="QConnect for GitLab",
        default_version='v1',
        description="API's for Merge Requests and Contributors!",
        terms_of_service="",
        contact=openapi.Contact(email="marginpatel@dal.ca"),
        license=openapi.License(name="MIT License"),
    )

schema_view = get_schema_view(
    swagger_info(),
    public=True,
    permission_classes=(AllowAny,),
)

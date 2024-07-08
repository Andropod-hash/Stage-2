from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import register, LoginView, UserViewDetail, OrganisationViewCreate, OrganizationDetailView, AddUserToOrganization

urlpatterns = [
    # Your API endpoints here...
    path('auth/register', register, name='register'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/login', LoginView.as_view(), name='login'),

    #  a user gets their own record or user record in organisations
    path("api/users/<uuid:pk>", UserViewDetail.as_view(), name="user-detail"),

    # gets all your organisations the user belongs to or created.

    path("api/organisations", OrganisationViewCreate.as_view(), name="creteOrgan"),

    # the logged in user gets a single organisation record
    path("api/organisations/<uuid:pk>", OrganizationDetailView.as_view(), name="organization-detail"),

    path('api/organisations/<uuid:orgId>/users', AddUserToOrganization.as_view(), name='add-user-to-organization'),
]


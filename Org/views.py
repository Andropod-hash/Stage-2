from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from django.contrib.auth import authenticate
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.serializers import Serializer
from .models import Organization, CustomUser
from .serializers import CustomUserSerializer, OrganisationSerializer, LoginSerializer, AddUserToOrganizationSerializer

class CustomSerializerErrorResponse:
    def __init__(self, serializer: Serializer): # Defines a custom class to handle serializer errors.
        self.serializer = serializer #The constructor method initializes the class with a serializer object, which contains validation errors.
    
    def format(self):
        formatted_errors = []
        for field, errors in self.serializer.errors.items():
            for error in errors:
                formatted_errors.append({"field": field, "message": error})
        return formatted_errors
    
    @property
    def response(self):
        return Response({"errors": self.format()}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

@swagger_auto_schema(method='post', request_body=CustomUserSerializer)
@api_view(['POST'])
def register(request):        
    serializer = CustomUserSerializer(data=request.data)
    if serializer.is_valid(raise_exception=False):
        try:
            user = serializer.save()
            # Create Organization
            organisation_name = f"{user.firstName}'s Organization"
            organization = Organization.objects.create(
                name=organisation_name,
                description="",
                created_by=user
            )
            user.organizations.add(organization)
            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Prepare response data
            user_data = CustomUserSerializer(user).data
            response_data = {
                'status': 'success',
                'message': 'Registration successful',
                'data': {
                    'accessToken': access_token,
                    'user': user_data,
                }
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "status": "Bad request",
                "message": "Registration unsuccessful",
                "statusCode": 400
            }, status=status.HTTP_401_UNAUTHORIZED)
    return CustomSerializerErrorResponse(serializer).response


class LoginView(APIView):
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(username=email, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                data = {
                    'status': 'success',
                    'message': 'Login successful',
                    'data': {
                        'accessToken': str(refresh.access_token),
                        'user': CustomUserSerializer(user).data
                    }
                }
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': 'Bad request',
                    'message': 'Authentication failed',
                    'statusCode': 401
                }, status=status.HTTP_401_UNAUTHORIZED)
        return CustomSerializerErrorResponse(serializer).response


# a user gets their own record or user record in organisations they belong to or created [PROTECTED].
class UserViewDetail(RetrieveAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = CustomUser.objects.get(userId=self.kwargs.get('pk'))
        if user is None:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        if user != self.request.user:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        response = CustomUserSerializer(user)
        if not response.data:
            return response 
        response_detail = {
            "status": "success",
            "message": "Retrieved user information successfully",
            "data": {
                "user": response.data,
            },
        }
        return Response(response_detail, status=status.HTTP_200_OK)


# the logged in user gets a single organisation record [PROTECTED]
class OrganizationDetailView(RetrieveAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        # Check if the user is either the creator or a member of the organization
        if obj.created_by != user and not obj.members.filter(userId=user.userId).exists():
            raise PermissionDenied("You do not have permission to access this organization.")
        return obj

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if not response.data:
            return response

        response_detail = {
            "status": "success",
            "message": "",
            "data": response.data
        }
        return Response(response_detail, status=status.HTTP_200_OK)

# a user can create their new organisation [PROTECTED].      
class OrganisationViewCreate(ListCreateAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Organization.objects.filter(
            Q(created_by=self.request.user) | Q(members__userId=self.request.user.userId)
        )

    def perform_create(self, serializer):
        user = self.request.user
        organization = serializer.save(created_by=user)
        user.organizations.add(organization)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=False):
            try:
                organization = serializer.save(created_by=request.user)
                response_data = {
                    "status": "success",
                    "message": "Organisation created successfully",
                    "data": {
                        "orgId": str(organization.orgId),  # Ensure orgId is a string
                        "name": organization.name,          # Ensure name is a string
                        "description": organization.description  # Ensure description is a string
                    },
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            except Exception:
                response_detail = {
                    "status": "Bad Request",
                    "message": "Client error",
                    "statusCode": 400
                }
                return Response(response_detail, status=status.HTTP_400_BAD_REQUEST)
        else:
            response_detail = {
                "status": "Bad Request",
                "message": "Validation error",
                "statusCode": 400,
                "errors": serializer.errors
            }
            return Response(response_detail, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response_detail = {
            "status": "success",
            "message": " retrieved successfully",
            "data": {
                "organisations": response.data,
            },
        }
        return Response(response_detail, status=status.HTTP_200_OK)

# 

class AddUserToOrganization(APIView):
    @swagger_auto_schema(request_body=AddUserToOrganizationSerializer)
    def post(self, request, orgId):
        try:
            organization = Organization.objects.get(orgId=orgId)
        except Organization.DoesNotExist:
            return Response({"status": "error", "message": f"Organization with ID {orgId} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        user_id = request.data.get('userId', None)
        if not user_id:
            return Response({"status": "error", "message": "userId field is required in the request body"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(userId=user_id)
            if organization.members.filter(userId=user_id).exists():
                return Response({"status": "error", "message": "User is already a member of this organization"}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({"status": "error", "message": f"User with ID {user_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        organization.members.add(user)
        return Response({"status": "success", "message": "User added to organization successfully"}, status=status.HTTP_200_OK)


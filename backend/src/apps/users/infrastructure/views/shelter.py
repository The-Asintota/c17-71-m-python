from rest_framework.serializers import Serializer
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import generics, status, exceptions
from typing import Dict, Any, List, Callable
from apps.users.infrastructure.serializers import ShelterSerializer
from apps.users.infrastructure.db import UserRepository
from apps.users.infrastructure.exceptions import NotAuthenticated
from apps.users.infrastructure.schemas.shelter import ShelterPostSchema
from apps.users.use_case import UserUsesCases
from apps.users.domain.constants import UserRoles


class ShelterAPIView(generics.GenericAPIView):
    """
    API view for managing operations for users with `shelter roles`.

    It uses a mapping approach to determine the appropriate application logic,
    permissions, and serializers based on the HTTP method of the incoming request.
    """

    application_class = UserUsesCases(user_repository=UserRepository)
    application_mapping = {
        "POST": application_class.register_user,
    }
    authentication_mapping = {
        "POST": [],
    }
    permission_mapping = {
        "POST": [],
    }
    serializer_mapping = {
        "POST": ShelterSerializer,
    }

    def get_authenticators(self):
        """
        Instantiates and returns the list of authenticators that this view can use.
        """

        try:
            authentication_classes = self.authentication_mapping[
                self.request.method
            ]
        except AttributeError:
            authentication_classes = []

        return [auth() for auth in authentication_classes]

    def get_permissions(self) -> List:
        """
        Get the permissions based on the request method.
        """

        try:
            permission_classes = self.permission_mapping[self.request.method]
        except KeyError:
            raise ValueError(f"Method {self.request.method} not allowed")

        return [permission() for permission in permission_classes]

    def get_serializer_class(self) -> Serializer:
        """
        Get the serializer class based on the request method.
        """

        try:
            serializer = self.serializer_mapping[self.request.method]
        except KeyError:
            raise ValueError(f"Method {self.request.method} not allowed")

        return serializer

    def get_application_class(self) -> Callable:
        """
        Get the application class based on the request method.
        """

        try:
            application_class = self.application_mapping[self.request.method]
        except KeyError:
            raise ValueError(f"Method {self.request.method} not allowed")

        return application_class

    def permission_denied(self, request: Request, message=None, code=None):
        """
        If request is not permitted, determine what kind of exception to raise.
        """

        if request.authenticators and not request.successful_authenticator:
            raise NotAuthenticated(code=code, detail=message)
        raise exceptions.PermissionDenied(code=code, detail=message)

    def _handle_valid_request(self, data: Dict[str, Any]) -> Response:
        application = self.get_application_class()
        application(data=data, role=UserRoles.SHELTER.value)

        return Response(status=status.HTTP_201_CREATED)

    @staticmethod
    def _handle_invalid_request(errors: List[Dict[str, List]]) -> Response:

        return Response(
            data={
                "code": "invalid_request_data",
                "detail": errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
            content_type="application/json",
        )

    @ShelterPostSchema
    def post(self, request: Request, *args, **kwargs) -> Response:
        """
        Handle POST requests for shelter registration.

        This method allows the registration of a new shelter. It waits for a POST
        request with a shelter's data, validates the information, and then creates
        a new record if the data is valid or returns an error response if it is not.
        """

        serializer_class = self.get_serializer_class()
        serializer: Serializer = serializer_class(data=request.data)

        if serializer.is_valid():
            return self._handle_valid_request(data=serializer.validated_data)

        return self._handle_invalid_request(errors=serializer.errors)

from rest_framework_simplejwt.authentication import (
    JWTAuthentication as BaseAuthentication,
    AuthUser,
)
from rest_framework_simplejwt.exceptions import (
    TokenError,
    InvalidToken,
    AuthenticationFailed,
)
from rest_framework_simplejwt.utils import get_md5_hash_password
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import Token
from apps.users.models import BaseUser


class JWTAuthentication(BaseAuthentication):
    """
    JWTAuthentication is a class that handles JSON web token authentication.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.user_model = BaseUser

    def get_validated_token(self, raw_token: bytes) -> Token:
        """
        Validates an encoded JSON web token and returns a validated token wrapper
        object.
        """

        messages = []
        for AuthToken in api_settings.AUTH_TOKEN_CLASSES:
            try:
                return AuthToken(raw_token)
            except TokenError as e:
                messages.append(
                    {
                        "token_type": AuthToken.token_type,
                        "message": e.args[0],
                    }
                )
        raise InvalidToken(code="authentication_failed", detail=messages)

    def get_user(self, validated_token: Token) -> AuthUser:
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken(
                detail="Token contained no recognizable user identification"
            )

        try:
            user = self.user_model.objects.get(uuid=user_id)
        except self.user_model.DoesNotExist:
            raise AuthenticationFailed(
                detail="User not found", code="user_not_found"
            )

        if not user.is_active:
            raise AuthenticationFailed(
                detail="User is inactive", code="user_inactive"
            )

        if api_settings.CHECK_REVOKE_TOKEN:
            if validated_token.get(
                api_settings.REVOKE_TOKEN_CLAIM
            ) != get_md5_hash_password(user.password):
                raise AuthenticationFailed(
                    detail="The user's password has been changed.",
                    code="password_changed",
                )

        return user

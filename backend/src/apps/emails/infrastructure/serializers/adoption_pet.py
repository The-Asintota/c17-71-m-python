from django.core.validators import RegexValidator
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from apps.emails.endpoint_schemas.adoption_pet import (
    AdoptionPetSerializerSchema,
)
from apps.users.infrastructure.serializers.constants import (
    COMMON_ERROR_MESSAGES,
)
from apps.utils import ErrorMessages


@AdoptionPetSerializerSchema
class AdoptionPetSerializer(ErrorMessages):
    """
    Defines the data required to send an email to the shelter when a user applies for
    adoption.
    """

    pet_name = serializers.CharField(
        error_messages={
            "invalid": COMMON_ERROR_MESSAGES["invalid"].format(
                field_name="El valor ingresado"
            ),
            "max_length": COMMON_ERROR_MESSAGES["max_length"].format(
                field_name="El valor ingresado", max_length="{max_length}"
            ),
        },
        required=True,
        max_length=50,
    )
    shelter_uuid = serializers.UUIDField(
        error_messages={
            "invalid": COMMON_ERROR_MESSAGES["invalid"].format(
                field_name="El id del refugio"
            ),
        },
        required=True,
    )
    user_name = serializers.CharField(
        error_messages={
            "invalid": COMMON_ERROR_MESSAGES["invalid"].format(
                field_name="El nombre"
            ),
            "max_length": COMMON_ERROR_MESSAGES["max_length"].format(
                field_name="El nombre", max_length="{max_length}"
            ),
        },
        required=True,
        max_length=50,
    )
    user_email = serializers.CharField(
        error_messages={
            "max_length": COMMON_ERROR_MESSAGES["max_length"].format(
                field_name="El correo electrónico", max_length="{max_length}"
            ),
        },
        required=True,
        max_length=40,
        validators=[
            RegexValidator(
                regex=r"^([A-Za-z0-9]+[-_.])*[A-Za-z0-9]+@[A-Za-z]+(\.[A-Z|a-z]{2,4}){1,2}$",
                code="invalid_data",
                message=COMMON_ERROR_MESSAGES["invalid"].format(
                    field_name="El correo electrónico"
                ),
            ),
        ],
    )
    user_phone = PhoneNumberField(
        required=True,
        error_messages={
            "invalid": COMMON_ERROR_MESSAGES["invalid"].format(
                field_name="El número de teléfono"
            ),
            "max_length": COMMON_ERROR_MESSAGES["max_length"].format(
                field_name="El número de teléfono", max_length="{max_length}"
            ),
        },
        max_length=25,
    )
    message = serializers.CharField(
        error_messages={
            "invalid": COMMON_ERROR_MESSAGES["invalid"].format(
                field_name="El valor ingresado"
            ),
            "max_length": COMMON_ERROR_MESSAGES["max_length"].format(
                field_name="El valor ingresado", max_length="{max_length}"
            ),
        },
        required=True,
        max_length=300,
    )

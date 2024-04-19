from django.contrib.auth.models import (
    AbstractBaseUser,
    UserManager,
    PermissionsMixin,
)
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from phonenumber_field.modelfields import PhoneNumberField
from uuid import uuid4, UUID


class CustomUserManager(UserManager):
    """
    UserManager is a class that provides helper functions to manage users.
    """

    def _create_base_user(
        self,
        uuid: UUID = None,
        email: str = None,
        password: str = None,
        **extra_fields,
    ):
        """
        Method that creates a base user, this is a helper method that helps in
        recording the `base information` of a user in the database.
        """

        user: AbstractBaseUser = self.model(
            uuid=uuid, email=self.normalize_email(email), **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_base_user(
        self,
        uuid: UUID = None,
        email: str = None,
        password: str = None,
        **extra_fields,
    ):
        """
        Create and save a base user, this is a helper method that helps in
        recording the `base information` of a user in the database.
        """

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)

        return self._create_base_user(
            uuid=uuid, email=email, password=password, **extra_fields
        )

    def create_superuser(
        self,
        uuid: UUID = None,
        email: str = None,
        password: str = None,
        **extra_fields,
    ):
        """
        Creates and saves a base user with `super user` role, this is an auxiliary
        method that helps in registering the `base information` of a user in the
        database.
        """

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if extra_fields.get("is_active") is not True:
            raise ValueError("Active user must have is_active=True.")

        return self._create_base_user(
            uuid=uuid,
            email=email,
            password=password,
            **extra_fields,
        )


class BaseUser(AbstractBaseUser, PermissionsMixin):
    """
    BaseUser is a model that represents the base information of each user in the
    system. This model is not just another type of user, but rather it contains the
    "base" information for each type of user.
    """

    uuid = models.UUIDField(db_column="uuid", primary_key=True, default=uuid4)
    email = models.EmailField(
        db_column="email",
        max_length=90,
        unique=True,
        db_index=True,
        blank=False,
        null=False,
    )
    password = models.CharField(
        db_column="password", max_length=128, blank=False, null=False
    )
    is_active = models.BooleanField(
        db_column="is active", default=False, db_index=True
    )
    is_staff = models.BooleanField(db_column="is_staff", default=False)
    is_superuser = models.BooleanField(db_column="is_superuser", default=False)
    last_login = models.DateTimeField(
        db_column="last login", blank=True, null=True
    )
    date_joined = models.DateTimeField(
        db_column="date joined", auto_now_add=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        db_table = "base_user"
        verbose_name = "Base user"
        verbose_name_plural = "Base users"
        ordering = ["is_active", "-date_joined"]
        indexes = [
            models.Index(
                fields=["email", "is_active"], name="email_is_active_idx"
            )
        ]

    def __str__(self):
        return self.uuid.__str__()


class Shelter(models.Model):
    """
    Shelter is a model that represents a type of user in the system.
    """

    base_user = models.OneToOneField(
        db_column="base_user",
        to="BaseUser",
        to_field="uuid",
        on_delete=models.CASCADE,
        primary_key=True,
    )
    shelter_name = models.CharField(
        db_column="shelter_name",
        max_length=50,
        unique=True,
        blank=False,
        null=False,
    )
    shelter_address = models.CharField(
        db_column="shelter_address", max_length=100, blank=False, null=False
    )
    shelter_phone_number = PhoneNumberField(
        db_column="shelter_phone_number",
        max_length=25,
        blank=False,
        null=False,
    )
    shelter_responsible = models.CharField(
        db_column="shelter_responsible", max_length=50, blank=False, null=False
    )
    shelter_logo = models.URLField(
        db_column="shelter_logo", max_length=200, blank=False, null=False
    )

    def __str__(self):
        return self.shelter_name

    class Meta:
        db_table = "shelter"
        verbose_name = "Shelter"
        verbose_name_plural = "Shelters"
        ordering = ["-base_user__date_joined"]


class AdminUser(models.Model):
    """
    AdminUser is a model that represents a type of user in the system.
    """

    base_user = models.OneToOneField(
        db_column="base_user",
        to="BaseUser",
        to_field="uuid",
        on_delete=models.CASCADE,
        primary_key=True,
    )
    admin_name = models.CharField(
        db_column="admin_name",
        max_length=50,
        unique=True,
        blank=False,
        null=False,
    )

    def __str__(self):
        return self.admin_name

    class Meta:
        db_table = "admin"
        verbose_name = "Admin"
        verbose_name_plural = "Admins"
        ordering = ["-base_user__date_joined"]


class UserDirectory(models.Model):
    """
    UserDirectory is a model that represents a list of all users in the system.
    """

    uuid = models.UUIDField(db_column="uuid", primary_key=True, default=uuid4)
    content_type = models.ForeignKey(to=ContentType, on_delete=models.CASCADE)
    user_uuid = models.UUIDField(
        db_column="user_uuid",
        null=False,
        blank=False,
        db_index=True,
        unique=True,
    )
    content_object = GenericForeignKey(
        ct_field="content_type", fk_field="user_uuid"
    )

    class Meta:
        db_table = "user_directory"
        verbose_name = "User directory"
        verbose_name_plural = "User directories"

    def __str__(self):
        return f"Object id {self.user_uuid} ({self.content_type})"


class JWT(models.Model):
    """
    This model is used to keep track of which tokens are associated with which
    users and which created tokens are pending expiration or invalidation.
    """

    jwt_uuid = models.UUIDField(
        db_column="jwt_uuid", primary_key=True, default=uuid4
    )
    content_type = models.ForeignKey(to=ContentType, on_delete=models.CASCADE)
    user_uuid = models.UUIDField(
        db_column="user_uuid",
        null=False,
        blank=False,
        db_index=True,
    )
    content_object = GenericForeignKey(
        ct_field="content_type", fk_field="user_uuid"
    )
    jti = models.CharField(
        db_column="jti",
        max_length=255,
        unique=True,
        db_index=True,
        null=False,
        blank=False,
    )
    token = models.TextField(db_column="token", null=False, blank=False)
    expires_at = models.DateTimeField(
        db_column="expires_at", null=False, blank=False
    )
    date_joined = models.DateTimeField(
        db_column="date joined", auto_now_add=True
    )

    class Meta:
        db_table = "jwt"
        verbose_name = "JWT"
        verbose_name_plural = "JWT's"
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        return "Token for {} ({})".format(
            self.user_uuid,
            self.jti,
        )


class JWTBlacklist(models.Model):
    """
    This model is used as a blacklist, it disables the added JSON Web Tokens so
    that they cannot be used for authentication purposes.
    """

    token_id = models.OneToOneField(
        db_column="token_id",
        to="JWT",
        to_field="jwt_uuid",
        on_delete=models.CASCADE,
        primary_key=True,
    )
    date_joined = models.DateTimeField(
        db_column="date_joined", auto_now_add=True
    )

    class Meta:
        db_table = "jwt_blacklist"
        verbose_name = "JWT blacklist"
        verbose_name_plural = "JWT blacklist"
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        return f"Blacklisted token for {self.token_id}"


class Pet(models.Model):
    """
    This model represents a shelter pet.
    """

    pet_uuid = models.UUIDField(
        db_column="pet_uuid", primary_key=True, default=uuid4
    )
    pet_type = models.ForeignKey(
        db_column="pet_type",
        to="PetType",
        to_field="id",
        on_delete=models.SET_NULL,
        null=True,
    )
    pet_sex = models.ForeignKey(
        db_column="pet_sex",
        to="PetSex",
        to_field="id",
        on_delete=models.SET_NULL,
        null=True,
    )
    shelter = models.ForeignKey(
        db_column="shelter",
        to="Shelter",
        to_field="base_user",
        on_delete=models.CASCADE,
    )
    pet_name = models.CharField(
        db_column="pet_name", max_length=50, blank=False, null=False
    )
    pet_race = models.CharField(
        db_column="pet_race", max_length=50, blank=False, null=False
    )
    pet_age = models.IntegerField(db_column="pet_age", blank=False, null=False)
    pet_observations = models.CharField(
        db_column="pet_observations",
        max_length=200,
        default="sin observaciones",
    )
    pet_description = models.CharField(
        db_column="pet_description",
        max_length=200,
        default="sin descripciones",
    )
    pet_image = models.URLField(
        db_column="pet_image",
        max_length=200,
        default="https://imagedefault.com",
    )
    date_joined = models.DateTimeField(
        db_column="date joined", auto_now_add=True
    )

    class Meta:
        db_table = "pet"
        verbose_name = "Pet"
        verbose_name_plural = "Pets"
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        return f"Pet {self.pet_name} from Shelter {self.shelter.shelter_name}"


class PetType(models.Model):
    """
    This model represents the type pet that is available in the system.
    """

    id = models.BigAutoField(db_column="id", primary_key=True)
    type = models.CharField(
        db_column="type", max_length=50, blank=False, null=False, unique=True
    )
    date_joined = models.DateTimeField(
        db_column="date joined", auto_now_add=True
    )

    class Meta:
        db_table = "pet_type"
        verbose_name = "Pet type"
        verbose_name_plural = "Pet types"
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        return f"Pet type {self.id}"


class PetSex(models.Model):
    """
    This model represents the type sex for pets that is available in the system.
    """

    id = models.BigAutoField(db_column="id", primary_key=True)
    sex = models.CharField(
        db_column="sex", max_length=50, blank=False, null=False, unique=True
    )
    date_joined = models.DateTimeField(
        db_column="date joined", auto_now_add=True
    )

    class Meta:
        db_table = "pet_sex"
        verbose_name = "Pet sex"
        verbose_name_plural = "Pet sexs"
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        return f"Sex type: {self.id}"

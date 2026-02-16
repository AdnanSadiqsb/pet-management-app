from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime
from .choices import Config_types, UserRole, ProjectStatus, TaskPeriority
from django.dispatch import receiver
from django.utils import timezone
import randomcolor
from django.contrib.postgres.fields import ArrayField

import uuid
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    role = models.CharField(
        max_length=200, choices=UserRole.choices, default=UserRole.ADMIN
    )
    avatar = models.FileField(upload_to="static/users_avatars", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    plain_password = models.CharField(max_length = 100, null=True, blank=True)
    phoneNumber = models.CharField(max_length=200, null=True, blank=True)
    first_name = None
    last_name = None
    username = models.CharField(max_length=100, unique=True) 
    is_sentMail = models.BooleanField(default=False)

    supplier = models.ForeignKey('self', on_delete=models.CASCADE, related_name='worker_supplier', null=True, blank=True)

    google_id = models.CharField(max_length=255, null=True, blank=True)
    apple_id = models.CharField(max_length=255, null=True, blank=True)

@receiver(models.signals.post_delete, sender=User)
def auto_delete_avatar(sender, instance, **kwargs):
    """
    Deletes avatar file from filesystem when corresponding `User` object is deleted.
    """
    if instance.avatar:
        if instance.avatar.storage.exists(instance.avatar.name):
            instance.avatar.storage.delete(instance.avatar.name)

class basedModel(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class typeOfConfig(basedModel):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=200, choices=Config_types.choices, default=Config_types.BREED)
    image = models.FileField(upload_to="static/type_of_config_images", blank=True, null=True)
    parent_type = models.ForeignKey('self', on_delete=models.CASCADE, related_name='sub_types', null=True, blank=True)

class Pet(basedModel):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets')
    age = models.IntegerField(default=0)
    breed = models.ForeignKey(typeOfConfig, on_delete=models.SET_NULL, related_name='pet_breed', null=True, blank=True)
    weight = models.FloatField(default=0.0)
    notes = models.TextField(null=True, blank=True)
    gender = models.CharField(max_length=200, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    health_status = models.CharField(max_length=200, null=True, blank=True)
    pet_type = models.ForeignKey(typeOfConfig, on_delete=models.SET_NULL, related_name='pet_type', null=True, blank=True)
    

class PetImage(basedModel):
    pet = models.ForeignKey(
        Pet,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.FileField(upload_to="pets/images/")
    

class PayPalPayment(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    amount =  models.FloatField(default=0.0)
    description = models.TextField(null=True, blank=True)
    response = models.JSONField(null=True, blank=True)
    PayementId  = models.CharField(max_length=300, null=True, blank=True)
    status  = models.CharField(null=True, blank=True, max_length=200, default='created')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='pay_created', null =True, blank=True)
    client = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='client_pay', null =True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=200, default='PayPal')
    checkoutLink  =models.CharField(max_length=600, null=True, blank=True)
    itemsList = models.JSONField(null=True, blank=True)
    enableTax = models.BooleanField(default=False)
    class Meta:
        ordering = ['-created_at']





class PetVisit(basedModel):
    VISIT_TYPE_CHOICES = [
        ("checkup", "Checkup"),
        ("emergency", "Emergency"),
        ("surgery", "Surgery"),
        ("grooming", "Grooming"),
        ("follow_up", "Follow Up"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("upcoming", "Upcoming"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)

    pet = models.ForeignKey(
        "Pet",
        on_delete=models.CASCADE,
        related_name="visits"
    )

    visit_type = models.CharField(
        max_length=50,
        choices=VISIT_TYPE_CHOICES,
        default="checkup"
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="upcoming"
    )

    visit_date = models.DateField()

    veterinarian_name = models.CharField(max_length=255)
    clinic_name = models.CharField(max_length=255, null=True, blank=True)

    # Medical Details
    diagnosis = models.TextField(null=True, blank=True)
    treatment = models.TextField(null=True, blank=True)
    prescriptions = models.TextField(null=True, blank=True)

    # Vitals
    weight = models.FloatField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)

    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.pet.name} - {self.visit_type} ({self.visit_date})"

class PetVaccination(basedModel):
    STATUS_CHOICES = [
        ("due", "Due"),
        ("completed", "Completed"),
        ("upcoming", "Upcoming"),
    ]

    CATEGORY_CHOICES = [
        ("core", "Core"),
        ("non_core", "Non-Core"),
        ("optional", "Optional"),
    ]

    ROUTE_CHOICES = [
        ("subcutaneous", "Subcutaneous"),
        ("intramuscular", "Intramuscular"),
        ("oral", "Oral"),
        ("intranasal", "Intranasal"),
        ("other", "Other"),
    ]

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)

    pet = models.ForeignKey(
        "Pet",
        on_delete=models.CASCADE,
        related_name="vaccinations"
    )

    vaccine_name = models.CharField(max_length=255)

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="due"
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="core"
    )

    date_given = models.DateField(null=True, blank=True)
    next_due_date = models.DateField(null=True, blank=True)

    veterinarian_name = models.CharField(max_length=255)
    clinic_name = models.CharField(max_length=255, null=True, blank=True)

    manufacturer = models.CharField(max_length=255, null=True, blank=True)
    batch_number = models.CharField(max_length=255, null=True, blank=True)

    dosage = models.CharField(max_length=100, null=True, blank=True)
    route = models.CharField(
        max_length=50,
        choices=ROUTE_CHOICES,
        null=True,
        blank=True
    )

    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.pet.name} - {self.vaccine_name}"

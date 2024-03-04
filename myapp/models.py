from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    score = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'auth_user'

    # Specify custom intermediary table names to avoid clashes
    groups = models.ManyToManyField(
        Group,
        through='MyAppUserGroups',
        related_name='custom_user_groups',
        related_query_name='custom_user_group',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        through='MyAppUserPermissions',
        related_name='custom_user_permissions',
        related_query_name='custom_user_permission',
        blank=True,
    )

class MyAppUserGroups(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    class Meta:
        db_table = 'myapp_user_groups'

class MyAppUserPermissions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        db_table = 'myapp_user_permissions'


class Tournament(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
from django.contrib import admin
from django.contrib.auth import get_user_model

from users.models import CustomUser, Subscription

User = get_user_model()


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'username',
                    'password',
                    'email',
                    'first_name',
                    'last_name'
                    )
    list_filter = ('username', 'email',)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)

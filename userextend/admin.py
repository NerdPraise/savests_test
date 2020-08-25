# Future modules

# Standard Library

# Third party libraries

# Django imports
from django.contrib import admin

# Local imports
from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "is_active",
                    "is_staff", "email", "date_joined")

    list_editable = ("email",)
    change_list_template = "admin/userextend/admin/change_list.html"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )
        try:
            queryset = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        # metrics = {
        #     "total": Count(id)
        # }
        response.context_data['data'] = list(
            queryset.values("id", "username", "is_active",
                            "is_staff", "email", "date_joined"
                            )
        )
        return response


# Reregister User model
# admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Future modules

# Standard Library

# Third party libraries

# Django imports
from django.contrib import admin
from django.db.models import Count, DateTimeField, Min, Max
from django.utils.translation import ngettext
from django.contrib import messages
from django.db.models.functions import Trunc

# Local imports
from .models import User


def get_next_in_date_hierarchy(request, date_hierarchy):
    if date_hierarchy + '__day' in request.GET:
        return 'hour'

    if date_hierarchy + '__month' in request.GET:
        return 'day'

    if date_hierarchy + '__year' in request.GET:
        return 'week'

    return 'day'


class UserAdmin(admin.ModelAdmin):
    """
    Model Admin for User
    """
    list_display = ("username", "is_active",
                    "is_staff", "email", "date_joined")
    change_list_template = "admin/userextend/admin/change_list.html"
    list_filter = ("date_joined", "is_active", "is_staff")
    actions = ("set_active", "set_inactive",)
    date_hierarchy = 'date_joined'

    def set_active(self, request, queryset):
        # Custom action option for setting user active
        updated = queryset.update(is_active=True)
        self.message_user(request, ngettext(
            '%d User was activated',
            '%d Users were activated',
            updated,
        ) % updated, messages.SUCCESS)

    def set_inactive(self, request, queryset):
        # Custom action option for setting user inactive
        updated = queryset.update(is_active=True)
        self.message_user(request, ngettext(
            '%d User is inactive',
            '%d Users are now inactive',
            updated,
        ) % updated, messages.SUCCESS)

    set_active.short_description = "Set users active"
    set_inactive.short_description = "Set users inactive"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )
        try:
            queryset = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        data = {
            "total": Count("id")
        }
        period = get_next_in_date_hierarchy(request, self.date_hierarchy)
        response.context_data['period'] = period
        users_over_time = queryset.annotate(
            period=Trunc(
                'date_joined',
                period,
                output_field=DateTimeField(),
            ),
        ).values('period').annotate(total=Count('id')).order_by('period')

        user_range = users_over_time.aggregate(
            low=Min('total'),
            high=Max('total'),
        )

        high = user_range.get('high', 0)
        low = user_range.get('low', 0)

        response.context_data['users_over_time'] = [{
            'period': x['period'],
            'total': x['total'] or 0,
            'pct': ((x['total'] or 0) - low) / (high - low) * 100
            if high > low else 0,
        } for x in users_over_time]

        response.context_data['total'] = dict(
            queryset.aggregate(**data)
        )
        return response


# Reregister User model
# admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Future modules

# Standard Library

# Third party libraries

# Django imports
from django.contrib import admin, messages
from django.core.mail import send_mass_mail
from django.db.models import Count, DateTimeField, Min, Max
from django.db.models.functions import Trunc
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.translation import ngettext
from django.urls import path

# Local imports
from .models import User
from .forms import SendMailForm


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
    change_list_template = "admin/userextend/change_list.html"
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

    def send_mail(self, request):
        """
        Method for mail sending functionality
        """
        if request.user.is_staff and request.user.is_superuser:
            form = SendMailForm()
            if request.method == "POST":
                form = SendMailForm(request.POST)
                if form.is_valid():
                    subject = form.cleaned_data.get("subject")
                    body = form.cleaned_data.get("body")

                    users = User.objects.all()  # To prevent hitting the db several times on the for loop
                    user_emails = [
                        user.email for user in users if user.email != ""]
                    message = (subject, body, "admin@admin.com", user_emails)
                    send_mass_mail((message,), fail_silently=False)
                    messages.success(request, "Messages sent Successfully")
                    form.save()  # optional
                    return redirect("admin:index")

            else:
                context = {
                    "form": form,
                    "user": request.user
                }
                return TemplateResponse(request, "userextend/send_mail.html", context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("send_mail", self.send_mail, name="send-mail"),
        ]
        return custom_urls + urls

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

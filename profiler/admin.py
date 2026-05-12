from django.contrib import admin
from django.utils.html import format_html
from .models import RequestMetric , EndpointSummary


@admin.register(RequestMetric)
class RequestMetricAdmin(admin.ModelAdmin):
    list_display = (
        "path",
        "method",
        "status_code",
        "colored_response_time",
        "query_count",
        "total_query_time_ms",
        "exception_type",
        "exception_message",
        "created_at",
    )

    list_filter = (
        "method",
        "status_code",
        "created_at"
    )

    readonly_fields = list_display

    ordering = ("-created_at",)

    def colored_response_time(self, obj):

        if obj.response_time_ms > 1000:
            color = "red"

        elif obj.response_time_ms > 500:
            color = "orange"

        else:
            color = "lightgreen"

        formatted_time = f"{obj.response_time_ms:.2f} ms"

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            formatted_time
        )
    

@admin.register(EndpointSummary)
class EndpointSummaryAdmin(admin.ModelAdmin):

    list_display = (
        "route",
        "window_start",
        "total_requests",
        "avg_response_ms",
        "p95_response_ms",
        "error_count",
        "slow_count",
    )

    list_filter = (
        "window_start",
        "computed_at",
    )

    search_fields = ("route",)

    ordering = ("-window_start",)

    readonly_fields = [field.name for field in EndpointSummary._meta.fields]

    date_hierarchy = "window_start"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
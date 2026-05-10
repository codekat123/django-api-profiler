from django.contrib import admin
from django.utils.html import format_html
from .models.request_metric import RequestMetric


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
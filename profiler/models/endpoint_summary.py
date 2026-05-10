from django.db import models 

class EndpointSummary(models.Model):
    route = models.CharField(max_length=500)
    window_start = models.DateTimeField()  
    window_end = models.DateTimeField()   

    total_requests = models.IntegerField(default=0)
    avg_response_ms = models.FloatField(default=0)
    p95_response_ms = models.FloatField(default=0)
    max_response_ms = models.FloatField(default=0)
    min_response_ms = models.FloatField(default=0)

    error_count = models.IntegerField(default=0)
    slow_count = models.IntegerField(default=0)
    n_plus_one_count = models.IntegerField(default=0)

    computed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("route", "window_start")  
        indexes = [
            models.Index(fields=["route", "window_start"]),
            models.Index(fields=["window_start"]),
        ]

    def __str__(self):
        return f"{self.route} | {self.window_start}"
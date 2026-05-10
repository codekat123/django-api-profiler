from django.db import models



class RequestMetric(models.Model):
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    status_code = models.IntegerField()
    response_time_ms = models.FloatField()
    query_count = models.IntegerField(default=0)
    total_query_time_ms = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_slow = models.BooleanField()
    has_exception = models.BooleanField(default=False)
    exception_type = models.CharField(max_length=255,null=True,blank=True)
    exception_message = models.TextField(null=True,blank=True)
    route = models.CharField(max_length=500, null=True, blank=True)
    view_name = models.CharField(max_length=255, null=True, blank=True)
    user_id = models.IntegerField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    request_id = models.UUIDField(null=True, blank=True)
    has_n_plus_one = models.BooleanField(default=False)
    n_plus_one_details = models.JSONField(null=True, blank=True)
    
    
    def __str__(self):
        return  f"{self.method} {self.path}"
        
    
    class Meta:
        indexes = [
            models.Index(fields=['route']),
            models.Index(fields=['status_code']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_slow']),
            models.Index(fields=['has_exception']),
        ]
    


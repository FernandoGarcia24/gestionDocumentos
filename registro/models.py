from django.db import models
from django.contrib.auth.models import User

class Document(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    pdf = models.FileField(upload_to='documents/')
    uploaded_by = models.ForeignKey(User, related_name='uploaded_documents', on_delete=models.CASCADE)
    approver = models.ForeignKey(User, related_name='approved_documents', on_delete=models.SET_NULL, null=True, blank=True)
    approved = models.BooleanField(null=True, blank=True)
    rejected = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
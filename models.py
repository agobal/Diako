from django.db import models
from django.contrib.auth.models import User

class Document(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')

class UserProfile(models.Model):
	user = models.OneToOneField(User)

	def __unicode__(self):
		return self.user.username
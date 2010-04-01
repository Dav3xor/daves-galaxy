from django.db import models

# Create your models here.

CATEGORY_CHOICES = (
  (1, 'editorial'),
  (2, 'sports'),
  (3, 'lighterside'),
  (4, 'crime'),
  (5, 'consumeradvocacy'),
  (6, 'lifestyle'),
  (7, 'entertainment'),
  (8, 'local'),
  (9, 'national'),
  (10, 'family'))


class Link(models.Model):
    link       = models.URLField           ('link', max_length=200)
    category   = models.IntegerField       ('category', choices=CATEGORY_CHOICES)
    posted     = models.DateTimeField      ('date published',auto_now_add=True)



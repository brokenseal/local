from django.db import models


class BaseManager(models.Manager):
    def as_dicts(self):
        queryset = self.get_query_set()
        # very simple representation, need to improve it
        return queryset.values(*[field.name for field in queryset.model._meta.fields])


class BaseModel(models.Model):
    objects = BaseManager()

    def as_dict(self):
        # very simple representation, need to improve it
        result = {}

        for field in self._meta.fields:
            result[field.name] = getattr(self, field.name)

        return result

    class Meta:
        abstract = True


class Message(BaseModel):
    author = models.CharField(max_length=200)
    text = models.TextField()

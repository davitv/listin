from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from datetime import timedelta


@python_2_unicode_compatible
class Task(models.Model):
    PRIORITY_CHOICES = (
        (0, "Unset",),
        (1, "Low",),
        (2, "Middle",),
        (3, "Hight",),
    )
    STATUS_CHOICES = (
        (0, "Unset",),
        (1, "Active",),
        (2, "Inactive",),
        (3, "Done",),
        (4, "Canceled",),
    )
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, null=False, related_name="added_by")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, )

    name = models.CharField(max_length=300, blank=False, null=False, )
    description = models.TextField(blank=True, null=True,)

    label = models.CharField(max_length=200, blank=True, null=False, default="unlabeled")

    priority = models.PositiveIntegerField(default=PRIORITY_CHOICES[0][0], blank=True, null=False,)
    status = models.PositiveIntegerField(default=STATUS_CHOICES[0][0], blank=True, null=False,)

    estimate_time = models.DurationField(_("planning time"), blank=True, null=True)
    original_time = models.DurationField(_("real spent time"), blank=True, null=True,)

    due_date = models.DateTimeField(_("until date"), blank=True, null=True,)

    date_started = models.DateTimeField(_("staring date"), blank=True, null=True, )
    date_finished = models.DateTimeField(_("end date"), blank=True, null=True, )

    date_added = models.DateTimeField(auto_now_add=True,)
    date_modified = models.DateTimeField(auto_now=True,)

    def __str__(self):
        return "%s" % (self.name, )

    def get_priority(self):
        return "%s" % (self.PRIORITY_CHOICES[self.priority][1])

    def get_status(self):
        return "%s" % (self.STATUS_CHOICES[self.status][1])

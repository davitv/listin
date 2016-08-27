from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django_countries.fields import CountryField


class UndefinedLevelException(Exception):
    pass


@python_2_unicode_compatible
class CV(models.Model):
    """
    Curriculum vitae model.
    Main one for which are above models.
    They will be included as many-to-many relations to CV.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, null=False)
    name = models.CharField(_("CV name"), max_length=300, blank=True, null=True)
    about = models.TextField(_("about me"), blank=True, null=True, )

    created_at = models.DateTimeField(auto_now_add=True,)
    modified_at = models.DateTimeField(auto_now=True,)

    class Meta:
        verbose_name_plural = _("CV")
        verbose_name = _("CVs")

    def __str__(self):
        return '%s (%s)' % (self.user.get_full_name(), self.modified_at)


@python_2_unicode_compatible
class Education(models.Model):
    """
    Education representing model.
    University name, specialization and degree should be unique
    together in order to do not create similar db records for
    people from same uni and faculty.
    """
    EDUCATION_DEGREE_CHOICES = (
        (0, _("unset"),),
        (1, _("bachelor"),),
        (2, _("Master"),),
        (3, _("Ph.D"),),
        (4, _("incomplete higher"),),
    )

    university = models.CharField(_("university name"), max_length=300, blank=False, null=False, )
    department = models.CharField(_("department name"), max_length=300, blank=False, null=False)
    specialization = models.CharField(_("profession/specialization"), max_length=300, blank=False, null=False,)

    degree = models.PositiveIntegerField(_("degree"),
                                         default=EDUCATION_DEGREE_CHOICES[0][0],
                                         choices=EDUCATION_DEGREE_CHOICES,
                                         blank=False, null=False,
                                         )
    cv = models.ForeignKey(CV, blank=False, null=False)

    class Meta:
        verbose_name_plural = _("Educations")
        verbose_name = _("Education")

    def __str__(self):
        return "%s (%s)" % (self.university, self.specialization,)


@python_2_unicode_compatible
class Experience(models.Model):
    """
    1. Products amount
    2. Rating
    3. Products Sellings
    4. Daily page views

    Experience is represented as a scope (string
    which names global industry scope, i.e. aviation,
    electromechanics, autoindustry...), specialization
    in selected industry (aviation - F12 jet pilot,
    IT - microscheme ingeneer)
    """
    cv = models.ForeignKey(CV, null=False, blank=False)
    organization = models.CharField(_("organization name"), max_length=300, blank=False, null=False)
    position = models.CharField(_("working position"), max_length=300, blank=True, null=True)

    region = CountryField(blank=True, null=True,)
    website = models.URLField(blank=True, null=True)

    date_from = models.DateField(_("date started to work"), blank=False, null=False,)
    date_to = models.DateField(_("date finished to work"), blank=False, null=False,)

    class Meta:
        verbose_name_plural = _("Experiences")
        verbose_name = _("Experience")

    def __str__(self):
        return "%s (%s)" % (self.specialization, self.scope,)


@python_2_unicode_compatible
class Language(models.Model):
    """
    Language knowledge levels.
    Code and level should be unique together
    because they probably would have a lot
    of common choices.
    """
    LANGUAGE_LEVELS = (
        (0, "Unset"),
        (1, "Elementary"),
        (2, "Intermediate"),
        (3, "Advanced"),
        (4, "Native"),
    )
    cv = models.ForeignKey(CV, blank=False, null=False, )
    name = models.CharField(_("language name"), max_length=200, blank=False, null=False,)
    level = models.PositiveIntegerField(_("knowledges level"), default=LANGUAGE_LEVELS[0][0], blank=False, null=False,
                                        choices=LANGUAGE_LEVELS)

    class Meta:
        verbose_name_plural = _("Languages")
        verbose_name = _("Language")

    def get_verbose_level(self):
        try:
            return self.LANGUAGE_LEVELS[self.level][1]
        except IndexError:
            raise UndefinedLevelException("There is no verbose level %s for language %s" %
                                          (self.level, self.name,))

    def __str__(self):
        return "%s (%s)" % (self.name, self.get_verbose_level())


@python_2_unicode_compatible
class Skill(models.Model):
    """
    Simple model representing skills.
    This probably would vary a lot for different people if
    level would be used, anyway it can also act as a tag-skills
    """
    SKILL_LEVEL_CHOICES = (
        (0, "Unset"),
        (1, "Elementary"),
        (2, "Intermediate"),
        (3, "Advanced"),
        (4, "Hardcore"),
    )
    cv = models.ForeignKey(CV, blank=False, null=False, )

    name = models.CharField(_("name"), max_length=200, blank=False, null=False,)
    level = models.PositiveIntegerField(_("experience/knowledges level"), default=SKILL_LEVEL_CHOICES[0][0], blank=True, null=False,)

    class Meta:
        verbose_name_plural = _("Skills")
        verbose_name = _("Skill")
        unique_together = ('name', 'cv', )

    def get_verbose_skill(self):
        try:
            return self.SKILL_LEVEL_CHOICES[self.level][1]
        except IndexError:
            raise UndefinedLevelException("There is no verbose level %s for skill %s" %
                                          (self.level, self.name,))

    def __str__(self):
        return '%s (%s)' % (self.name, self.get_verbose_skill())


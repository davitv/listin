from django.contrib import admin
from jobs.models import CV, Education, Language, Skill


class EducationAdmin(admin.ModelAdmin):
    pass


class SkillAdmin(admin.ModelAdmin):
    pass


class LanguageAdmin(admin.ModelAdmin):
    pass


class EducationInline(admin.TabularInline):
    model = Education


class CVAdmin(admin.ModelAdmin):
    inlines = [
        EducationInline
    ]


admin.site.register(CV, CVAdmin)
admin.site.register(Education, EducationAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(Language, LanguageAdmin)

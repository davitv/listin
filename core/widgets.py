from django.forms import ClearableFileInput, CheckboxInput
from django.utils.html import conditional_escape, mark_safe
from django.utils.translation import ugettext_lazy as _


class PreviewImageWidget(ClearableFileInput):

    initial_text = _('Currently')
    input_text = _('Upload image')
    clear_checkbox_label = _('Clear')

    template_with_initial = (
        '<div class="upload-preview">'
            '<div class="upload-preview-wrapper"></div>'
            '<input type="hidden" value="%(initial_url)s" class="upload-preview-url">'
            '<label for="%(input_id)s" class="upload-preview-file-label">'
                '%(input_text)s'
                '<input name="%(name)s" type="file" class="upload-preview-fileinput"  id="%(input_id)s" />'
            '</label>'
            '<label for="%(clear_checkbox_id)s"  class="upload-preview-remove">'
                '<input id="%(clear_checkbox_id)s" name="%(name)s-clear" type="checkbox" class="upload-preview-clear" />'
                '<span class="upload-preview-remove-btn">X</span>'
            '</label>'
        '</div>'
    )

    class Media:
        js = ('profiles/js/upload-preview.js',)
        css = {
            'all': ('profiles/css/upload-preview.css',)
        }

    def get_template_substitution_values(self, value):
        """
        Return value-related substitutions.
        """
        return {
            'initial': conditional_escape(value) if value else '',
            'initial_url': conditional_escape(value.url) if value else '',
        }

    def render(self, name, value, attrs=None):
        template = self.template_with_initial
        checkbox_name = self.clear_checkbox_name(name)
        checkbox_id = self.clear_checkbox_id(checkbox_name)

        substitutions = {'initial_text': self.initial_text,
                         'input_text': self.input_text,
                         'clear_template': '',
                         'clear_checkbox_label': self.clear_checkbox_label,
                         'input': super(ClearableFileInput, self).render(name, value, attrs),
                         'input_id': attrs['id'],
                         'name': name,
                         'clear_checkbox_name': conditional_escape(checkbox_name),
                         'clear_checkbox_id': conditional_escape(checkbox_id),
                         'clear': CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id}),
                         }
        substitutions.update(self.get_template_substitution_values(value))

        return mark_safe(template % substitutions)




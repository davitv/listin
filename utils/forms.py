

def get_field_type(field):
    return field.__class__.__name__


def form_to_dict(form):
    ret = {}
    field_items = form.fields.items()
    for k, v in field_items:
        ret[k] = {
            'name': k,
            'value': '',
            'type': get_field_type(v),
            'required': v.required,
        }
        if getattr(v, 'choices', False):
            ret[k]['choices'] = v.choices
        if getattr(v, 'input_formats', False):
            ret[k]['input_formats'] = v.input_formats

    return ret

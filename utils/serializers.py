from rest_framework import serializers


class ConcatenatedListField(serializers.CharField):
    """
    Field that handles concatenated list by desired
    separator and child attribute is a field, to which
    will be splitted values passed on by one for validation.
    """

    # default is an integer because usually it represents
    # primary keys
    child = serializers.IntegerField()

    def __init__(self, separator=',', child=None, to_repr=None, **kwargs):
        self.separator = separator
        self.to_repr = to_repr
        if child:
            self.child = child
        super(ConcatenatedListField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        value = super(ConcatenatedListField, self).to_internal_value(data)
        return [self.child.run_validation(item) for item in value.split(self.separator)]

    def to_representation(self, value):
        repr_function = self.to_repr or self.child.to_representation
        return [repr_function(item) for item in value]

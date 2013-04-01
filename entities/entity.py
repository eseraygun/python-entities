from basic import PRIMARY, MultipleErrors, ValidationError
from field import Field
from schema import Schema


class Entity(object):
    __metaclass__ = Schema

    # noinspection PyArgumentList
    def __new__(cls, *args, **kwargs):
        self = super(Entity, cls).__new__(cls, *args, **kwargs)
        self._values = dict()
        return self

    def __init__(self, *args, **kwargs):
        # Check positional arguments.
        if len(args) > len(self._fields):
            raise TypeError(
                '__init__() takes at most %d arguments (%d given)'
                % (len(self._fields), len(args))
            )

        # Check keyword arguments.
        for name in kwargs:
            if name not in self._fields:
                raise TypeError(
                    '%r is an invalid keyword argument for this function'
                    % name
                )

        # Initialize values.
        for index, (name, field) in enumerate(self._fields.iteritems()):
            if index < len(args):
                self._values[name] = args[index]
            elif name in kwargs:
                self._values[name] = kwargs[name]

    def _get_value(self, name):
        if name in self._values:
            return self._values[name]
        else:
            value = self._fields[name].make_default()
            self._values[name] = value
            return value

    def validate(self):
        errors = []
        for name, field in self._fields.iteritems():
            try:
                field.validate(self._get_value(name))
            except ValidationError, ex:
                errors.append(ex)

        if len(errors) == 1:
            raise errors[0]
        elif len(errors) > 1:
            raise MultipleErrors(None, self, errors)

    def keyify(self, group=PRIMARY, child_group=None):
        if child_group is None:
            child_group = group

        return tuple(field.keyify(self._get_value(field.name), child_group)
                     for field in self._groups[group])

    def __repr__(self):
        fields = self._groups.get(PRIMARY)
        if fields is None:
            fields = self._fields.itervalues()

        args = ', '.join('%s=%r' % (field.name, self._get_value(field.name))
                         for field in fields)

        return '%s(%s)' % (self.__class__.__name__, args)


class EntityField(Field):
    base_class = Entity

    def __init__(self, entity_class, default=None, null=True, group=None):
        super(EntityField, self).__init__(default, null, group)
        self.base_class = entity_class

    def validate(self, value):
        super(EntityField, self).validate(value)

        if value is not None:
            value.validate()

    def keyify(self, value, group=PRIMARY):
        if value is None:
            return None
        else:
            return value.keyify(group)


class ReferenceField(Field):
    base_class = Entity

    def __init__(self, entity_class, reference_group=PRIMARY,
                 default=None, null=True, group=None):
        super(ReferenceField, self).__init__(default, null, group)
        self.base_class = entity_class
        self.reference_group = reference_group

    def make_empty(self):
        return None

    def keyify(self, value, group=PRIMARY):
        if value is None:
            return None
        else:
            return value.keyify(self.reference_group, group)

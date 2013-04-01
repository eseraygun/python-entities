import itertools
import datetime
import pytz
from basic import PRIMARY, ValidationError, MultipleErrors


_field_count = itertools.count()


class Field(object):
    base_class = None

    def __init__(self, default=None, null=True, group=None):
        global _field_count
        self.index = _field_count.next()
        self.container = None
        self.name = None
        self.default = default
        self.null = null
        self.group = group

    def make_default(self):
        if self.default is None:
            if self.null:
                default = None
            else:
                default = self.make_empty()
        elif callable(self.default):
            default = self.default()
        else:
            default = self.default

        if not self.null and default is None:
            raise ValueError('non-nullable field initialized as None')

        return default

    def make_empty(self):
        if self.base_class is None:
            return None
        else:
            return self.base_class()

    def full_name(self):
        if self.container is None:
            return self.name
        else:
            return '%s.%s' % (self.container.full_name(), self.name)

    def validate(self, value):
        if value is None:
            if not self.null:
                raise ValidationError(self, value, 'null value')
        else:
            if self.base_class is not None \
                    and not isinstance(value, self.base_class):
                raise ValidationError(self, value, 'invalid type')

    # noinspection PyUnusedLocal
    def keyify(self, value, group=PRIMARY):
        return value

    # noinspection PyUnusedLocal
    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return instance._get_value(self.name)

    def __set__(self, instance, value):
        instance._values[self.name] = value

    def __repr__(self):
        return '%s(name=%r)' % (self.__class__.__name__, self.name)


class DynamicField(Field):
    base_class = object

    def __init__(self, base_class=object, default=None, null=True, group=None):
        super(DynamicField, self).__init__(default, null, group)
        self.base_class = base_class


class BooleanField(Field):
    base_class = bool


class IntegerField(Field):
    base_class = int


class FloatField(Field):
    base_class = float


class StringField(Field):
    base_class = basestring

    def make_empty(self):
        return u''


class DateField(Field):
    base_class = datetime.date

    def make_empty(self):
        return pytz.utc.localize(datetime.datetime.utcnow()).date()


class TimeField(Field):
    base_class = datetime.datetime

    def make_empty(self):
        return pytz.utc.localize(datetime.datetime.utcnow())


class CollectionField(Field):
    key_class = tuple

    def __init__(self, item_field=None, recursive=False,
                 default=None, null=True, group=None):
        super(CollectionField, self).__init__(default, null, group)

        self.item_field = item_field
        if self.item_field is not None:
            self.item_field.name = '<item>'
            self.item_field.container = self

        self.recursive = recursive

    def _items_of(self, value):
        return value

    def _item_field_of(self, item):
        if self.recursive and isinstance(item, self.base_class):
            return self
        else:
            return self.item_field

    def validate(self, value):
        super(CollectionField, self).validate(value)

        # Validate items.
        if value is not None and self.item_field is not None:
            errors = []
            for item in self._items_of(value):
                try:
                    self._item_field_of(item).validate(item)
                except ValidationError, ex:
                    errors.append(ex)
            if len(errors) == 1:
                raise errors[0]
            elif len(errors) > 1:
                raise MultipleErrors(self, value, errors)

    def keyify(self, value, group=PRIMARY):
        if value is None:
            return None
        elif self.item_field is None:
            return self.key_class(self._items_of(value))
        else:
            return self.key_class(self._item_field_of(item).keyify(item, group)
                                  for item in self._items_of(value))


class ListField(CollectionField):
    base_class = list


class SetField(CollectionField):
    base_class = set
    key_class = frozenset


class DictField(CollectionField):
    base_class = dict
    key_class = tuple

    def _items_of(self, value):
        return value.itervalues()

    def keyify(self, value, group=PRIMARY):
        if value is None:
            return None
        elif self.item_field is None:
            return self.key_class(sorted(value.iteritems()))
        else:
            return self.key_class(sorted(
                (key, self._item_field_of(item).keyify(item, group))
                for key, item in value.iteritems()
            ))

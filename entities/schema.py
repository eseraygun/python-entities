from collections import OrderedDict
from field import Field


class Schema(type):

    def __new__(mcs, name, bases, attrs):
        cls = super(Schema, mcs).__new__(mcs, name, bases, attrs)

        fields = [(name, field) for name, field in attrs.iteritems()
                  if isinstance(field, Field)]
        fields.sort(key=lambda item: item[1].index)
        cls._fields = OrderedDict(fields)

        for name, field in cls._fields.iteritems():
            field.name = name

        cls._groups = dict()
        for field in cls._fields.itervalues():
            if field.group is not None:
                group_fields = cls._groups.get(field.group)
                if group_fields is None:
                    cls._groups[field.group] = [field]
                else:
                    group_fields.append(field)

        return cls

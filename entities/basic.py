PRIMARY = 0
SECONDARY = 1


class ValidationError(Exception):

    def __init__(self, field, value, reason):
        self.field = field
        self.value = value
        self.reason = reason

    def __repr__(self):
        return '%s(%r, %r, %r)' % (self.__class__.__name__,
                                   self.field, self.value, self.reason)

    def __str__(self):
        return '%s = %r (%s)' % (self.field.full_name(), self.value,
                                 self.reason)

    def __unicode__(self):
        return u'%s = %r (%s)' % (self.field.full_name(), self.value,
                                  self.reason)


class MultipleErrors(ValidationError):

    def __init__(self, field, value, errors):
        super(MultipleErrors, self).__init__(field, value, 'multiple errors')
        self.errors = errors

    def __str__(self):
        return '\n'.join(str(error) for error in self.errors)

    def __unicode__(self):
        return u'\n'.join(unicode(error) for error in self.errors)

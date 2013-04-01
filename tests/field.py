import unittest
from entities import *


class TestField(unittest.TestCase):

    def test_make_default(self):
        field = Field(default=None, null=True)
        self.assertEqual(field.make_default(), None)

        field = Field(default=lambda: 1, null=True)
        self.assertEqual(field.make_default(), 1)

        field = Field(default=2, null=True)
        self.assertEqual(field.make_default(), 2)

        field = Field(default=None, null=False)
        self.assertRaises(ValueError, field.make_default)

    def test_full_name(self):
        class Foo(Entity):
            field = ListField(DynamicField())
        self.assertEqual(Foo.field.full_name(), 'field')
        self.assertEqual(Foo.field.item_field.full_name(), 'field.<item>')

    def test_validate(self):
        field = Field(null=True)
        self.assertEqual(field.validate(None), None)

        field = DynamicField(IntegerField, null=True)
        self.assertEqual(field.validate(None), None)

        field = DynamicField(IntegerField, null=False)
        self.assertRaises(ValidationError, lambda: field.validate(None))
        self.assertRaises(ValidationError, lambda: field.validate(1.0))

    def test_keyify(self):
        field = Field()
        self.assertEqual(field.keyify(None), None)
        self.assertEqual(field.keyify(1), 1)
        self.assertEqual(field.keyify('foo'), 'foo')

    def test_get_set(self):
        class Foo(Entity):
            field = IntegerField(0)
        self.assertIsInstance(Foo.field, Field)

        entity = Foo()
        self.assertIsInstance(entity.field, int)

        entity.field = 1
        self.assertEqual(entity.field, 1)

    def test_repr(self):
        class Foo(Entity):
            field = Field()
        self.assertEqual(repr(Foo.field), "Field(name='field')")


class TestDynamicField(unittest.TestCase):

    def test_make_empty(self):
        empty = DynamicField().make_empty()
        self.assertIsInstance(empty, object)


class TestBooleanField(unittest.TestCase):

    def test_make_empty(self):
        empty = BooleanField().make_empty()
        self.assertIsInstance(empty, bool)
        self.assertEqual(empty, False)


class TestIntegerField(unittest.TestCase):

    def test_make_empty(self):
        empty = IntegerField().make_empty()
        self.assertIsInstance(empty, int)
        self.assertEqual(empty, 0)


class TestFloatField(unittest.TestCase):

    def test_make_empty(self):
        empty = FloatField().make_empty()
        self.assertIsInstance(empty, float)
        self.assertEqual(empty, 0.0)


class TestStringField(unittest.TestCase):

    def test_make_empty(self):
        empty = StringField().make_empty()
        self.assertIsInstance(empty, basestring)
        self.assertEqual(empty, u'')


class TestDateField(unittest.TestCase):

    def test_make_empty(self):
        empty = DateField().make_empty()
        self.assertIsInstance(empty, datetime.date)


class TestTimeField(unittest.TestCase):

    def test_make_empty(self):
        empty = TimeField().make_empty()
        self.assertIsInstance(empty, datetime.datetime)


class TestCollectionField(unittest.TestCase):

    def test_make_empty(self):
        empty = ListField().make_empty()
        self.assertIsInstance(empty, list)
        self.assertEqual(len(empty), 0)

    def test_validate(self):
        field = ListField()
        self.assertEqual(field.validate([1, 2.0, '3']), None)

        field = ListField(IntegerField())
        self.assertEqual(field.validate([1, 2, 3]), None)
        self.assertRaises(ValidationError,
                          lambda: field.validate([1, 2, '3']))
        self.assertRaises(MultipleErrors,
                          lambda: field.validate([1, 2.0, '3']))

        field = ListField(IntegerField(), recursive=True)
        self.assertEqual(field.validate([1, [2, 3]]), None)
        self.assertRaises(ValidationError,
                          lambda: field.validate([1, [2, '3']]))
        self.assertRaises(MultipleErrors,
                          lambda: field.validate([1, [2.0, '3']]))

    def test_keyify(self):
        field = ListField()
        self.assertEqual(field.keyify(None), None)
        self.assertEqual(field.keyify([1, 2, 3]), (1, 2, 3))

        field = ListField(ListField())
        self.assertEqual(field.keyify(None), None)
        self.assertEqual(field.keyify([[1], [2, 3]]), ((1,), (2, 3)))


class TestListField(unittest.TestCase):

    def test_make_empty(self):
        empty = ListField().make_empty()
        self.assertIsInstance(empty, list)
        self.assertEqual(len(empty), 0)


class TestSetField(unittest.TestCase):

    def test_make_empty(self):
        empty = SetField().make_empty()
        self.assertIsInstance(empty, set)
        self.assertEqual(len(empty), 0)


class TestDictField(unittest.TestCase):

    def test_make_empty(self):
        empty = DictField().make_empty()
        self.assertIsInstance(empty, dict)
        self.assertEqual(len(empty), 0)

    def test_validate(self):
        field = DictField(IntegerField())
        self.assertEqual(field.validate({'1': 1}), None)

    def test_keyify(self):
        field = DictField()
        self.assertEqual(field.keyify(None), None)
        self.assertEqual(field.keyify({'1': 1, '2': 2}), (('1', 1), ('2', 2)))

        field = DictField(DictField())
        self.assertEqual(field.keyify(None), None)
        self.assertEqual(
            field.keyify({'1': {'1.1': 11}, '2': {'2.1': 21}}),
            (('1', (('1.1', 11),)), ('2', (('2.1', 21),)))
        )


if __name__ == '__main__':
    unittest.main()

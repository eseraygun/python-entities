import unittest
from entities import *


class TestEntity(unittest.TestCase):

    def test_init(self):
        class Foo(Entity):
            id = IntegerField()
            name = StringField()
            desc = StringField()
        self.assertRaises(TypeError, lambda: Foo(1, '2', '3', 4.0))
        self.assertRaises(TypeError, lambda: Foo(1, '2', '3', zirt=4.0))

        entity = Foo(1, desc='3')
        self.assertEqual(entity.id, 1)
        self.assertEqual(entity.name, None)
        self.assertEqual(entity.desc, '3')

    def test_validate(self):
        class Foo(Entity):
            id = IntegerField()

        class Bar(Entity):
            id = IntegerField()
            child = EntityField(Foo)

        entity = Bar()
        self.assertEqual(entity.validate(), None)

        entity.child = Foo()
        self.assertEqual(entity.validate(), None)

        entity.id = '1'
        self.assertRaises(ValidationError, entity.validate)

        entity.child.id = '2'
        self.assertRaises(MultipleErrors, entity.validate)

    def test_keyify(self):
        class Foo(Entity):
            id = IntegerField(group=PRIMARY)
            name = StringField(group='secondary')

        class Bar(Entity):
            id_1 = IntegerField(group=PRIMARY)
            id_2 = EntityField(Foo, group=PRIMARY)
            name = StringField(group='secondary')

        entity = Bar()
        self.assertEqual(entity.keyify(), (None, None))

        entity = Bar(1, Foo(2, 'foo'), 'bar')
        self.assertEqual(entity.keyify(), (1, (2,)))
        self.assertEqual(entity.keyify('secondary'), ('bar',))
        self.assertEqual(entity.keyify(PRIMARY, 'secondary'), (1, ('foo',)))

    def test_repr(self):
        class Foo(Entity):
            id = IntegerField(0)
            name = StringField('foo')
        self.assertEqual(repr(Foo()), "Foo(id=0, name='foo')")

        class Foo(Entity):
            id = IntegerField(0, group=PRIMARY)
            name = StringField('foo')
        self.assertEqual(repr(Foo()), "Foo(id=0)")


class TestReferenceField(unittest.TestCase):

    def test_make_empty(self):
        empty = ReferenceField(Entity).make_empty()
        self.assertIs(empty, None)

    def test_keyify(self):
        class Foo(Entity):
            id = IntegerField(group=PRIMARY)
            name = StringField(group='secondary')

        class Bar(Entity):
            id_1 = IntegerField(group=PRIMARY)
            id_2 = ReferenceField(Foo, reference_group='secondary',
                                  group=PRIMARY)

        entity = Bar()
        self.assertEqual(entity.keyify(), (None, None))

        entity = Bar(1, Foo(2, 'foo'))
        self.assertEqual(entity.keyify(), (1, ('foo',)))
        self.assertEqual(entity.keyify(PRIMARY, PRIMARY), (1, ('foo',)))


if __name__ == '__main__':
    unittest.main()

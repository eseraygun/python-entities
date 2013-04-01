from entities import *


class Account(Entity):
    id = IntegerField(group=PRIMARY)  # this field is in primary key group
    iban = IntegerField(group=SECONDARY)  # this is in secondary key group
    balance = FloatField(default=0.0)


class Name(Entity):
    first_name = StringField(group=SECONDARY)
    last_name = StringField(group=SECONDARY)


class Customer(Entity):
    id = IntegerField(group=PRIMARY)
    name = EntityField(Name, group=SECONDARY)
    accounts = ListField(ReferenceField(Account), default=[])


# Create Account objects.
a_1 = Account(1, 111, 10.0)  # __init__() recognize positional arguments
a_2 = Account(id=2, iban=222, balance=20.0)  # as well as keyword arguments

# Generate hashable key using primary key.
print a_1.keyify()  # prints '(1,)'

# Generate hashable key using secondary key.
print a_2.keyify(SECONDARY)  # prints '(222,)'

# Create Customer object.
c = Customer(1, Name('eser', 'aygun'))

# Generate hashable key using primary key.
print c.keyify()  # prints '(1,)'

# Generate hashable key using secondary key.
print c.keyify(SECONDARY)  # prints '(('eser', 'aygun'),)'

# Try validating an invalid object.
c.accounts.append(123)
try:
    c.validate()  # fails
except ValidationError:
    print 'accounts list is only for Account objects'

# Try validating a valid object.
c.accounts = [a_1, a_2]
c.validate()  # succeeds

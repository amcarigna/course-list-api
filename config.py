from peewee import SqliteDatabase

DEBUG = True

# don't let reviews be posted without a corresponding course already in existence
# so we are enforcing foreignkey
DATABASE = SqliteDatabase('courses.sqlite', pragmas={'foreign_keys': 1})

DEFAULT_RATE = "60/hour"


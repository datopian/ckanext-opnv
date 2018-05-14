import uuid
import logging

import sqlalchemy as sa
from sqlalchemy import func

import ckan.logic as logic
import ckan.model as model

user_extra = None
log = logging.getLogger(__name__)
NotFound = logic.NotFound

__all__ = ['UserExtra', 'user_extra', ]


def uuid4():
    return str(uuid.uuid4())


def setup():
    if user_extra is None:
        define_user_extra_table()
        log.debug('User extra table defined in memory')

        if not user_extra.exists():
            user_extra.create()
    else:
        log.debug('User extra table already exist')


class UserExtra(model.DomainObject):

    @classmethod
    def get(cls, user_id, key, default=None):
        '''Finds a single entity in the register.'''
        kw = {'user_id': user_id, 'key': key}
        query = model.Session.query(cls).autoflush(False)
        result = query.filter_by(**kw).first()
        if result:
            return result
        else:
            return default

    @classmethod
    def extra_exists(cls, key):
        """Returns true if there is an extra field with the same key."""
        query = model.Session.query(cls).autoflush(False)
        return query.filter(func.lower(cls.key) == func.lower(key)).first() is not None

    @classmethod
    def delete(cls, user_id, key):
        """Deletes single instance."""
        kwds = {'user_id': user_id, 'key': key}
        obj = model.Session.query(cls).filter_by(**kwds).first()
        if not obj:
            raise NotFound
        model.Session.delete(obj)
        model.Session.commit()


def define_user_extra_table():
    global user_extra
    user_extra = sa.Table('user_extra', model.meta.metadata,
                          sa.Column('id', sa.types.UnicodeText,
                                    primary_key=True, default=uuid4),
                          sa.Column('user_id', sa.types.UnicodeText,
                                    sa.ForeignKey('user.id')),
                          sa.Column('key', sa.types.UnicodeText), sa.Column(
                              'value', sa.types.UnicodeText),
                          sa.Column('state', sa.types.UnicodeText,
                                    default=u'active'),
                          )
    model.meta.mapper(UserExtra, user_extra)

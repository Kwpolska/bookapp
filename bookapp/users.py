# -*- encoding: utf-8 -*-
# Bookapp v0.1.0
# A library management app.
# Copyright © 2016-2018, Chris Warrick.
# See /LICENSE for licensing information.

"""
User management.

:Copyright: © 2016-2018, Chris Warrick.
:License: BSD (see /LICENSE).
"""

from passlib.apps import custom_app_context as pwd_context
from bookapp import db_conn

__all__ = ('create_user', 'login',)


def create_user(username, password, firstname, lastname):
    """Create an user."""
    pwd_hash = pwd_context.encrypt(password)
    with db_conn.cursor() as cur:
        cur.execute("""
            INSERT INTO AdminUser (username, password, firstname, lastname)
            VALUES (%s, %s, %s, %s)""", (username, pwd_hash, firstname, lastname))
        db_conn.commit()


def login(username, password):
    """Log into a user account."""
    with db_conn.cursor() as cur:
        cur.execute("""
            SELECT id, password, firstname, lastname FROM AdminUser
            WHERE username = %s;""", (username,))
        row = cur.fetchone()
    if not row:
        raise Exception("No such user")
    id, pwd_hash, firstname, lastname = row
    if pwd_context.verify(password, pwd_hash):
        return {
            'username': username,
            'id': id,
            'firstname': firstname,
            'lastname': lastname
        }
    else:
        raise Exception("Invalid password")

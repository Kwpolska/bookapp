# -*- encoding: utf-8 -*-
# Bookapp v0.1.0
# A library management app.
# Copyright © 2016-2018, Chris Warrick.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the author of this software nor the names of
#    contributors to this software may be used to endorse or promote
#    products derived from this software without specific prior written
#    consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
A library management app.

:Copyright: © 2016-2018, Chris Warrick.
:License: BSD (see /LICENSE).
"""

import psycopg2

__title__ = 'Bookapp'
__version__ = '0.1.0'
__author__ = 'Chris Warrick'
__license__ = '3-clause BSD'
__docformat__ = 'restructuredtext en'

__all__ = ('db_conn',)

db_conn = psycopg2.connect(
    dbname='bookapp', user='bookapp', password='bookapp')

book_rentals = """
SELECT book_copy_id, Book.title,
       Patron.firstname, Patron.lastname,
       rental_date, return_by FROM Rental
JOIN BookCopy ON BookCopy.id = book_copy_id
JOIN Patron on Patron.id = patron_id
JOIN Book ON BookCopy.book_id = Book.id
"""
category_tables = {'A': 'Author', 'B': 'Book', 'C': 'BookCopy', 'P': 'Patron',
                   'U': 'AdminUser'}

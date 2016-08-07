# -*- encoding: utf-8 -*-
# Bookapp v0.1.0
# A library management app.
# Copyright © 2016, Chris Warrick.
# See /LICENSE for licensing information.

"""
CLI utilities for Bookapp.

:Copyright: © 2016, Chris Warrick.
:License: BSD (see /LICENSE).
"""

import bookapp.users
import getpass
from bookapp import db_conn, book_rentals, category_tables

__all__ = ('cli_main', 'print_book_row', 'print_book_copy_row', 'ask_yesno', 'editors')


def cli_main():
    """CLI version of Bookapp’s interface."""
    print("Welcome to Bookapp!")
    cur = db_conn.cursor()

    cur.execute("SELECT COUNT(*) FROM AdminUser;")
    if not cur.fetchone()[0]:
        print("WARNING: no user accounts exist. Creating new account:")
        has_users = False
    else:
        has_users = True

    username = input("Username: ")
    password = getpass.getpass()
    if not has_users:
        _firstname = input("First name: ")
        _lastname = input("Last name: ")

        bookapp.users.create_user(username, password, _firstname, _lastname)

    user_data = bookapp.users.login(username, password)

    print("Welcome, {0} {1} (U{2})!".format(
        user_data['firstname'], user_data['lastname'], user_data['id']))
    print("Type letter + ID or an action.")
    print("Actions: L — list all, M — manage, O — overdue, S — search, Q — quit")
    while True:
        db_conn.commit()
        action = input('\n> ').upper()
        try:
            item_id = int(action[1:])
        except ValueError:
            item_id = None
        if action.startswith('M'):
            print("Actions: N — add, E — edit, D – delete, Q — cancel")
            print("Categories: A – author, B — book, C — copy, "
                  "P — patron, U — admin user")
            actionitem = input("Action Item/Category> ").strip().upper()
            if not actionitem or actionitem == 'Q':
                continue
            try:
                action = actionitem[0]
                item = actionitem[1:].strip()
                item_cat = item[0]
            except IndexError:
                print("Invalid syntax.")
                continue
            try:
                item_id = int(item[1:])
            except ValueError:
                item_id = ''

            if item_cat not in category_tables:
                print("Invalid item.")
                continue

            if action == 'N':
                new_id = editors[item_cat](db_conn, None)
                print("Created {0}{1}.".format(item_cat, new_id))
            elif action == 'E':
                new_id = editors[item_cat](db_conn, item_id)
                print("Edited {0}{1}.".format(item_cat, new_id))
            elif action == 'D':
                cur.execute("DELETE FROM {0} WHERE id = %s;".format(
                    category_tables[item_cat]), (item_id,))
                db_conn.commit()
            else:
                print("Unknown action.")
        elif action.startswith('O'):
            db_conn.commit()
            cur.execute(
                book_rentals + "WHERE returned IS NULL AND "
                "return_by < CURRENT_TIMESTAMP;")
            if cur.rowcount:
                print("Overdue books:")
                for row in cur:
                    print("C{0} {1} (patron: {2} {3})\n     rented on {4}, "
                          "return date {5}".format(*row))
            else:
                print("No overdue books.")
        elif action.startswith('Q'):
            print("Goodbye!")
            cur.close()
            return 0
        elif action.startswith('P'):
            # Patron number
            cur.execute("""
                SELECT firstname, lastname, dob, rental_limit FROM Patron
                WHERE id = %s""", (item_id,))
            if not cur.rowcount:
                print("Unknown patron.")
                continue
            print("{0} {1}\nDOB: {2}\nRental limit: {3}".format(
                *cur.fetchone()))
            print("Books:")
            cur.execute(book_rentals + 'WHERE patron_id = %s '
                        'AND returned IS NULL', (item_id,))
            if not cur.rowcount:
                print("No books.")
            for row in cur:
                print("C{0} {1}\n     rented on {4}, return date {5}".format(
                      *row))
        elif action.startswith('C'):
            # book Copy number
            cur.execute(
                """SELECT BookCopy.id, book_id, Book.title,
                            Author.firstname, Author.lastname
                FROM BookCopy
                JOIN Book on book_id = Book.id
                JOIN Author on Book.author_id = Author.id
                WHERE BookCopy.id = %s""", (item_id,))
            if not cur.rowcount:
                print("Book copy doesn’t exist.")
                continue
            print("{2}  by {3} {4} (C{0}/B{1})".format(*cur.fetchone()))
            cur.execute(
                book_rentals + 'WHERE book_copy_id = %s '
                'AND returned IS NULL', (item_id,))
            if cur.rowcount:
                row = cur.fetchone()
                print("Rented by {2} {3} on {4}, return date {5}".format(
                    *row))
                ret = ask_yesno("Return?", default=True)
                if ret:
                    cur.execute(
                        """UPDATE Rental SET returned = CURRENT_TIMESTAMP
                        WHERE returned IS NULL;""")
            else:
                print("Available for rental")
                while True:
                    ret = input("Rent to whom? ")
                    if (not ret) or ret.lower().startswith('p'):
                        break
                if not ret:
                    continue
                patron = int(ret[1:])
                cur.execute("SELECT COUNT(*) FROM Rental "
                            "WHERE patron_id = %s AND returned IS NULL",
                            (patron,))
                has_books = cur.fetchone()[0]
                cur.execute("SELECT rental_limit FROM Patron "
                            "WHERE id = %s""", (patron,))
                try:
                    limit = cur.fetchone()[0]
                except TypeError:
                    print("Patron doesn’t exist.")
                    continue
                if has_books >= limit:
                    print("Error: rental limit exceeded ({0}/{1})".format(
                        has_books, limit))
                    continue
                cur.execute(
                    "INSERT INTO Rental (book_copy_id, patron_id, "
                    "rental_date, return_by) VALUES (%s, %s, "
                    "CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + interval '14 "
                    "days') RETURNING return_by",
                    (item_id, patron))
                print("Book has to be returned by {0}".format(
                    cur.fetchone()[0]))

        elif action.startswith('B'):
            # Book number
            cur.execute("SELECT title, Author.firstname, Author.lastname, "
                        "isbn FROM Book JOIN Author on author_id = Author.id "
                        "WHERE Book.id = %s", (item_id,))
            row = cur.fetchone()
            if row:
                print("{0}  by {1} {2}".format(*row))
                print("ISBN: {0}".format(row[3]))
                cur.execute("SELECT CONCAT('C', id) FROM BookCopy "
                            "WHERE book_id = %s", (item_id,))
                print("Copies: " + ", ".join(i[0] for i in cur))
            else:
                print("Book doesn’t exist.")

        elif action.startswith('A'):
            # Author number
            cur.execute("SELECT firstname, lastname FROM Author "
                        "WHERE id = %s", (item_id,))
            row = cur.fetchone()
            if row:
                print("Author {0} {1}".format(*row))
                cur.execute("SELECT id, title FROM Book WHERE author_id = %s",
                            (item_id,))
                if cur.rowcount:
                    print("Books:")
                else:
                    print("No books.")
                for row in cur:
                    print("B{0} {1}".format(*row))
            else:
                print("Author doesn’t exist.")

        elif action.startswith('U'):
            # admin User number
            cur.execute("SELECT username, firstname, lastname FROM AdminUser "
                        "WHERE id = %s", (item_id,))
            row = cur.fetchone()
            if row:
                print("User {0} — {1} {2}".format(*row))
            else:
                print("User doesn’t exist.")
        elif action.startswith('S'):
            category = input("Category [ABPU]: ").upper()
            query = '%' + input("Query: ").strip() + '%'
            if category == 'B':
                # Search books for title and ISBN
                cur.execute(
                    "SELECT Book.id, title, Author.firstname, "
                    "Author.lastname FROM Book JOIN Author on author_id = "
                    "Author.id WHERE title ILIKE %s OR isbn ILIKE %s",
                    (query, query))
                if not cur.rowcount:
                    print("No results.")
                for row in cur:
                    print("B{0} {1}  by {2} {3}".format(*row))
                continue
            elif category == 'U':
                extra_fields = ', username'
                extra_where = 'OR username ILIKE %s'
                search_fstr = "{0}{1} {2} {3} ({4})"
                search_params = (query, query)
            else:
                extra_fields = extra_where = ''
                search_params = (query,)
                search_fstr = "{0}{1} {2} {3}"

            cur.execute(
                "SELECT id, firstname, lastname{0} FROM {1} WHERE "
                "CONCAT(firstname, ' ', lastname) ILIKE %s{2}".format(
                    extra_fields, category_tables[category], extra_where),
                search_params)
            if not cur.rowcount:
                print("No results.")
            for row in cur:
                print(search_fstr.format(category, *row))
        elif action.startswith('L'):
            category = input("Category [ABPU]: ").upper()
            cur.execute("SELECT id, firstname, lastname FROM {0}".format(
                category_tables[category]))
            if not cur.rowcount:
                print("No results.")
            for row in cur:
                print("{0}{1} {2} {3}".format(category, *row))
        else:
            print("Unknown action.")
    cur.close()


def print_book_row(id, title):
    print("B{0} {1}".format(id, title))


def print_book_copy_row(id, copy_id, title):
    print("B{0} C{1} {2}".format(id, copy_id, title))


def ask_yesno(query, default=None):
    """Ask a yes/no question."""
    if default is None:
        default_q = ' [y/n]'
    elif default is True:
        default_q = ' [Y/n]'
    elif default is False:
        default_q = ' [y/N]'
    inp = input("{query}{default_q} ".format(query=query,
                                             default_q=default_q)).strip()
    if inp:
        return inp.lower().startswith('y')
    elif default is not None:
        return default
    else:
        # Loop if no answer and no default.
        return ask_yesno(query, default)


def editor_ui(orig_fields, db_data=None):
    """Generic UI for an editor."""
    field_letters = {}
    fields = []
    if db_data is not None:
        for fi, fd in zip(orig_fields, db_data):
            fi[3] = fd
            new_fi = fi.copy()
            fields.append(new_fi)
    else:
        fields = orig_fields
    for fi in fields:
        field_letters[fi[0]] = fi

    print("Type letter to edit or press Enter to finish editing")
    inp = 'x'
    while inp:
        for letter, sqlfield, friendlyname, value in fields:
            print("[{0}] {1}: {2}".format(letter, friendlyname, value))
        inp = input('Field> ')
        if inp:
            new_value = input("New value> ")
            field_letters[inp][-1] = new_value
    return fields


def generic_editor(db_conn, fields, sqlfields, table, id=None):
    """Edit data for a DB entry."""
    if id is not None:
        with db_conn.cursor() as cur:
            cur.execute("SELECT {0} FROM {1} WHERE id = %s".format(
                sqlfields, table), (id,))
            db_data = cur.fetchone()
            fields = fields
            new_fields = editor_ui(fields, db_data)
            update_stmts = []
            update_values = []
            for old_data, new_data in zip(fields, new_fields):
                if old_data[3] != new_data[3]:
                    print(old_data[3], new_data[3])
                    update_values.append(new_data[3])
                    update_stmts.append("{0} = %s".format(new_data[1]))
            update_values.append(id)
            if update_stmts:
                cur.execute("UPDATE {0} SET {1} WHERE id = %s".format(
                    table, ', '.join(update_stmts)), update_values)
                db_conn.commit()
            return id
    else:
        db_data = None
        new_fields = editor_ui(fields, db_data)
        sql_fields = []
        sql_placeholders = []
        sql_values = []
        for letter, sqlfield, friendlyname, value in fields:
            sql_fields.append(sqlfield)
            sql_placeholders.append('%s')
            sql_values.append(value)
        # Special casing for user’s password
        if table == 'AdminUser':
            sql_fields.append('password')
            sql_placeholders.append('%s')
            sql_values.append('UNSET')

        with db_conn.cursor() as cur:
            cur.execute(
                "INSERT INTO {0} ({1}) VALUES ({2}) RETURNING id".format(
                    table, ','.join(sql_fields), ','.join(sql_placeholders)),
                sql_values)
            db_conn.commit()
            return cur.fetchone()[0]


def edit_author(db_conn, id=None):
    """Edit author data."""
    fields = (
        ['f', 'firstname', 'First name', ''],
        ['l', 'lastname', 'Last name', ''],
    )
    sqlfields = 'firstname, lastname'
    table = 'Author'
    return generic_editor(db_conn, fields, sqlfields, table, id)


def edit_book(db_conn, id=None):
    """Edit book data."""
    fields = (
        ['t', 'title', 'Title', ''],
        ['a', 'author_id', 'Author ID', ''],
        ['i', 'isbn', 'ISBN', '']
    )
    sqlfields = 'title, author_id, isbn'
    table = 'Book'
    return generic_editor(db_conn, fields, sqlfields, table, id)


def edit_book_copy(db_conn, id=None):
    """Edit book copy data."""
    with db_conn.cursor() as cur:
        if id is None:
            book_id = input("Book ID: ")
            cur.execute("INSERT INTO BookCopy (book_id) VALUES (%s) "
                        "RETURNING id", (book_id,))
            print("Created C{0}".format(cur.fetchone()[0]))
        else:
            cur.execute("SELECT book_id from BookCopy WHERE id = %s", (id,))
            book_id = cur.fetchone()[0]
            book_id = input("Book ID (currently {0}): ".format(book_id))
            if book_id:
                cur.execute("UPDATE BookCopy set book_id = %s "
                            "WHERE id = %s", (book_id, id))
        db_conn.commit()


def edit_patron(db_conn, id=None):
    """Edit patron data."""
    fields = (
        ['f', 'firstname', 'First name', ''],
        ['l', 'lastname', 'Last name', ''],
        ['d', 'dob', 'DOB', ''],
        ['r', 'rental_limit', 'Rental limit', ''],
    )
    sqlfields = 'firstname, lastname, dob, rental_limit'
    table = 'Patron'
    return generic_editor(db_conn, fields, sqlfields, table, id)


def edit_user(db_conn, id=None):
    """Edit user data."""
    print("User data:")
    fields = (
        ['f', 'firstname', 'First name', ''],
        ['l', 'lastname', 'Last name', ''],
        ['u', 'username', 'User name', ''],
    )
    sqlfields = 'firstname, lastname, username'
    table = 'AdminUser'
    new_id = generic_editor(db_conn, fields, sqlfields, table, id)
    if id is None:
        change_password = True
    else:
        change_password = ask_yesno("Change password?")

    if change_password:
        password = getpass.getpass("Password: ")
        pwd_hash = bookapp.users.pwd_context.encrypt(password)
        cur = db_conn.cursor()
        cur.execute("UPDATE AdminUser SET password = %s WHERE id = %s",
                    (pwd_hash, id))
        db_conn.commit()
        cur.close()

    return new_id


editors = {
    'A': edit_author,
    'B': edit_book,
    'C': edit_book_copy,
    'P': edit_patron,
    'U': edit_user
}

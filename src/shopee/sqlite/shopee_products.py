import sqlite3


def connect_database():
    con = sqlite3.connect('shopee_products.sqlite')
    return con


def create_table():
    try:
        with connect_database() as conn:
            sql = '''CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY,userid INTEGER NOT NULL, itemid INTEGER NOT NULL, shopid INTEGER NOT NULL, count INTEGER NOT NULL, UNIQUE(userid, itemid, shopid))'''
            conn.execute(sql)
            conn.commit()
            print('Created table')
    except Exception as err:
        print(err)


def insert_product(product):
    inserted_product = {}
    try:
        with connect_database() as conn:
            cur = conn.cursor()
            sql = '''INSERT INTO products (userid, itemid, shopid, count) VALUES (?,?,?,5)'''
            param = [product['userid'], product['itemid'], product['shopid']]
            cur.execute(sql, param)
            conn.commit()
            inserted_product = get_product_by_id(cur.lastrowid)
            print('saved product')
    except Exception as err:
        conn.rollback()
        inserted_product = None
        print(err)
    return inserted_product


def update_product(product):
    updated_product = {}
    try:
        with connect_database() as conn:
            cur = conn.cursor()
            sql = '''UPDATE products SET userid = ?, itemid = ?, shopid = ?, count = ? WHERE id = ?'''
            param = (product['userid'], product['itemid'],
                     product['shopid'], product['count'], product['id'])
            cur.execute(sql, param)
            conn.commit()
            updated_product = get_product_by_id(product['id'])
            print('updated product')
    except Exception as err:
        conn.rollback()
        updated_product = None
        print(err)
    return updated_product


def delete_product(id: int):
    message = {}
    try:
        with connect_database() as conn:
            sql = '''DELETE FROM products WHERE id = ?'''
            param = [id]
            conn.execute(sql, param)
            conn.commit()
            message['status'] = 'product deleted successfully'
            print(f'deleted product {id})')
    except Exception as err:
        conn.rollback()
        message = None
        print(err)
    return message


def get_product_by_id(id: int):
    product = {}
    try:
        with connect_database() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            sql = '''SELECT * FROM products WHERE id = ?'''
            param = [id]
            cur.execute(sql, param)
            row = cur.fetchone()

            product['id'] = row['id']
            product['userid'] = row['userid']
            product['itemid'] = row['itemid']
            product['shopid'] = row['shopid']
            product['count'] = row['count']

            print('get one product by id')
    except Exception as err:
        product = None
        print(err)
    return product


def get_products():
    products = []
    try:
        with connect_database() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            sql = '''SELECT * FROM products'''
            cur.execute(sql)
            rows = cur.fetchall()
            for row in rows:
                product = {}
                product['id'] = row['id']
                product['userid'] = row['userid']
                product['itemid'] = row['itemid']
                product['shopid'] = row['shopid']
                product['count'] = row['count']
                products.append(product)
        print('get all products')
    except Exception as err:
        products = None
        print(err)
    return products

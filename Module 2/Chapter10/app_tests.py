import os
from my_app import app, db
import unittest2 as unittest
import tempfile
from geoip import IPInfo
from mock import patch
import coverage

cov = coverage.coverage(
    omit = [
        '/Users/shalabhaggarwal/workspace/mydev/lib/python2.7/site-packages/*',
        'app_tests.py'
    ]
)
cov.start()


class CatalogTestCase(unittest.TestCase):

    def setUp(self):
        self.test_db_file = tempfile.mkstemp()[1]
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + self.test_db_file
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        self.lookup_patcher = patch('geoip.geolite2.lookup', autospec=True)
        PatchedLookup = self.lookup_patcher.start()
        PatchedLookup.return_value = IPInfo('17.0.0.1', {
            'location': {
                'time_zone': 'America/Los_Angeles'
            }
        })
        db.create_all()

    def tearDown(self):
        self.lookup_patcher.stop()
        os.remove(self.test_db_file)

    def test_home(self):
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 200)

    def test_products(self):
        "Test Products list page"
        rv = self.app.get('/en/products')
        self.assertEqual(rv.status_code, 200)
        self.assertTrue('No Previous Page' in rv.data)
        self.assertTrue('No Next Page' in rv.data)

    def test_create_category(self):
        "Test creation of new category"
        rv = self.app.get('/en/category-create')
        self.assertEqual(rv.status_code, 200)

        rv = self.app.post('/en/category-create')
        self.assertEqual(rv.status_code, 200)
        self.assertTrue('This field is required.' in rv.data)

        rv = self.app.get('/en/categories')
        self.assertEqual(rv.status_code, 200)
        self.assertFalse('Phones' in rv.data)

        rv = self.app.post('/en/category-create', data={
            'name': 'Phones',
        })
        self.assertEqual(rv.status_code, 302)

        rv = self.app.get('/en/categories')
        self.assertEqual(rv.status_code, 200)
        self.assertTrue('Phones' in rv.data)

        rv = self.app.get('/en/category/1')
        self.assertEqual(rv.status_code, 200)
        self.assertTrue('Phones' in rv.data)

    def test_create_product(self):
        "Test creation of new product"
        rv = self.app.get('/en/product-create')
        self.assertEqual(rv.status_code, 200)

        rv = self.app.post('/en/product-create')
        self.assertEqual(rv.status_code, 200)
        self.assertTrue('This field is required.' in rv.data)

        # Create a category to be used in product creation
        rv = self.app.post('/en/category-create', data={
            'name': 'Phones',
        })
        self.assertEqual(rv.status_code, 302)

        rv = self.app.post('/en/product-create', data={
            'name': 'iPhone 5',
            'price': 549.49,
            'company': 'Apple',
            'category': 1
        })
        self.assertEqual(rv.status_code, 302)

        rv = self.app.get('/en/product/1')
        self.assertEqual(rv.status_code, 200)
        self.assertTrue('iPhone 5' in rv.data)
        self.assertTrue('America/Los_Angeles' in rv.data)

    def test_search_product(self):
        "Test searching product"
        # Create a category to be used in product creation
        rv = self.app.post('/en/category-create', data={
            'name': 'Phones',
        })
        self.assertEqual(rv.status_code, 302)

        # Create a product
        rv = self.app.post('/en/product-create', data={
            'name': 'iPhone 5',
            'price': 549.49,
            'company': 'Apple',
            'category': 1
        })
        self.assertEqual(rv.status_code, 302)

        # Create another product
        rv = self.app.post('/en/product-create', data={
            'name': 'Galaxy S5',
            'price': 549.49,
            'company': 'Samsung',
            'category': 1
        })
        self.assertEqual(rv.status_code, 302)

        self.app.get('/')

        rv = self.app.get('/en/product-search?name=iPhone')
        self.assertEqual(rv.status_code, 200)
        self.assertTrue('iPhone 5' in rv.data)
        self.assertFalse('Galaxy S5' in rv.data)

        rv = self.app.get('/en/product-search?name=iPhone 6')
        self.assertEqual(rv.status_code, 200)
        self.assertFalse('iPhone 6' in rv.data)


if __name__ == '__main__':
    try:
        unittest.main()
    finally:
        cov.stop()
        cov.save()
        cov.report()
        cov.html_report(directory = 'coverage')
        cov.erase()

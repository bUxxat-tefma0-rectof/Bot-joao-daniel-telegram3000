import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.validators import validate_phone, validate_email, validate_amount
from utils.string_utils import StringUtils
from utils.date_utils import DateUtils
from utils.security import Security

class TestValidators(unittest.TestCase):
    def test_validate_phone_valid(self):
        self.assertTrue(validate_phone('11999998888'))
    
    def test_validate_phone_invalid(self):
        self.assertFalse(validate_phone('123'))
    
    def test_validate_email_valid(self):
        self.assertTrue(validate_email('test@test.com'))
    
    def test_validate_email_invalid(self):
        self.assertFalse(validate_email('invalid'))
    
    def test_validate_amount_valid(self):
        self.assertTrue(validate_amount(50, 0, 100))
    
    def test_validate_amount_invalid(self):
        self.assertFalse(validate_amount(200, 0, 100))

class TestStringUtils(unittest.TestCase):
    def test_remove_accents(self):
        result = StringUtils.remove_accents('coração')
        self.assertEqual(result, 'coracao')
    
    def test_slugify(self):
        result = StringUtils.slugify('Olá Mundo!')
        self.assertEqual(result, 'ola-mundo')
    
    def test_truncate(self):
        result = StringUtils.truncate('Hello World', 8)
        self.assertEqual(len(result), 8)
    
    def test_mask_email(self):
        result = StringUtils.mask_email('test@email.com')
        self.assertIn('***', result)
    
    def test_random_string(self):
        result = StringUtils.random_string(10)
        self.assertEqual(len(result), 10)

class TestDateUtils(unittest.TestCase):
    def test_now(self):
        result = DateUtils.now()
        self.assertIsNotNone(result)
    
    def test_today(self):
        result = DateUtils.today()
        self.assertIsNotNone(result)
    
    def test_format_date(self):
        from datetime import datetime
        result = DateUtils.format_date(datetime(2024, 1, 15))
        self.assertEqual(result, '15/01/2024')
    
    def test_is_expired(self):
        from datetime import datetime, timedelta
        past = datetime.now() - timedelta(days=1)
        self.assertTrue(DateUtils.is_expired(past))
        future = datetime.now() + timedelta(days=1)
        self.assertFalse(DateUtils.is_expired(future))

class TestSecurity(unittest.TestCase):
    def test_hash_text(self):
        result = Security.hash_text('test')
        self.assertEqual(len(result), 64)
    
    def test_generate_token(self):
        result = Security.generate_token(16)
        self.assertEqual(len(result), 32)
    
    def test_sanitize_input(self):
        result = Security.sanitize_input('<script>alert("xss")</script>')
        self.assertNotIn('<script>', result)
    
    def test_generate_password(self):
        result = Security.generate_password(12)
        self.assertEqual(len(result), 12)

if __name__ == '__main__':
    unittest.main()

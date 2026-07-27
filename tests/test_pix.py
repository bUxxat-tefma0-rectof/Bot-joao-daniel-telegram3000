import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.pix_service import PixService

class TestPixService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ps = PixService()
    
    def test_gerar_pix_structure(self):
        result = self.ps.gerar_pix(123456, 10, "Teste")
        self.assertIsInstance(result, dict)
        self.assertIn('sucesso', result)
    
    def test_verificar_pix_structure(self):
        result = self.ps.verificar("test_id")
        self.assertIsInstance(result, dict)
        self.assertIn('sucesso', result)
    
    def test_pix_invalid_token(self):
        ps = PixService()
        ps.token = "invalid_token"
        result = ps.gerar_pix(123456, 10)
        self.assertFalse(result['sucesso'])

if __name__ == '__main__':
    unittest.main()

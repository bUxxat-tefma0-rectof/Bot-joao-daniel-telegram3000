import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestHandlers(unittest.TestCase):
    def setUp(self):
        self.update = MagicMock()
        self.context = MagicMock()
        self.update.effective_user = MagicMock()
        self.update.effective_user.id = 123456
        self.update.effective_user.first_name = 'Test'
        self.update.effective_user.username = 'testuser'
    
    def test_start_handler_structure(self):
        from handlers.client_handler import start
        self.assertTrue(callable(start))
    
    def test_callback_handler_structure(self):
        from handlers.client_handler import callback
        self.assertTrue(callable(callback))
    
    def test_handle_msg_structure(self):
        from handlers.client_handler import handle_msg
        self.assertTrue(callable(handle_msg))
    
    def test_admin_handler_structure(self):
        from handlers.admin_handler import admin
        self.assertTrue(callable(admin))
    
    def test_adm_callback_structure(self):
        from handlers.admin_handler import adm_callback
        self.assertTrue(callable(adm_callback))
    
    def test_gen_pix_structure(self):
        from handlers.client_handler import gen_pix
        self.assertTrue(callable(gen_pix))
    
    def test_build_keyboard_structure(self):
        from handlers.client_handler import build_kb
        self.assertTrue(callable(build_kb))
    
    def test_payment_handler(self):
        from handlers.payment_handler import process_payment
        self.assertTrue(callable(process_payment))
    
    def test_cart_handler(self):
        from handlers.cart_handler import add_to_cart, view_cart, clear_cart, checkout
        self.assertTrue(callable(add_to_cart))
        self.assertTrue(callable(view_cart))
        self.assertTrue(callable(clear_cart))
        self.assertTrue(callable(checkout))
    
    def test_search_handler(self):
        from handlers.search_handler import start_search, do_search
        self.assertTrue(callable(start_search))
        self.assertTrue(callable(do_search))
    
    def test_conversion_handler(self):
        from handlers.conversion_handler import start_conversion, process_conversion
        self.assertTrue(callable(start_conversion))
        self.assertTrue(callable(process_conversion))
    
    def test_gift_handler(self):
        from handlers.gift_handler import redeem_gift_start, redeem_gift_process
        self.assertTrue(callable(redeem_gift_start))
        self.assertTrue(callable(redeem_gift_process))
    
    def test_ranking_handler(self):
        from handlers.ranking_handler import show_rankings, show_ranking_detail
        self.assertTrue(callable(show_rankings))
        self.assertTrue(callable(show_ranking_detail))
    
    def test_command_handler(self):
        from handlers.command_handler import cmd_pix, cmd_saldo, cmd_id, cmd_historico
        self.assertTrue(callable(cmd_pix))
        self.assertTrue(callable(cmd_saldo))
        self.assertTrue(callable(cmd_id))
        self.assertTrue(callable(cmd_historico))
    
    def test_error_handler(self):
        from handlers.error_handler import error_handler
        self.assertTrue(callable(error_handler.handle_error))

if __name__ == '__main__':
    unittest.main()

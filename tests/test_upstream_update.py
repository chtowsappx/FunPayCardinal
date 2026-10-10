"""Offline regression checks for the upstream update and fork compatibility."""
import configparser
import concurrent.futures
import pathlib
import tempfile
import unittest
import requests
from types import SimpleNamespace
from unittest.mock import Mock, patch

from FunPayAPI import Account, types
from FunPayAPI.common.enums import Currency, OrderStatuses
from FunPayAPI.common.exceptions import UnauthorizedError
from FunPayAPI.common.utils import strip_invisible_suffix, parse_currency
from Utils import cardinal_tools, config_loader
import first_setup
import handlers
from tg_bot import file_uploader, keyboards, static_keyboards
from tg_bot.bot import TGBot


class UpdateRegressionTests(unittest.TestCase):
    def test_profile_retains_fork_fields_when_parsed(self):
        account = Account('test')
        account._Account__initiated = True
        html = '''<body data-app-data='{"csrf-token": "test"}'>
        <div class="user-link-name">seller</div><span class="mr4">seller</span>
        <span class="media-user-status">Онлайн</span>
        <div class="avatar-photo" style="background:url(/photo.jpg)"></div>
        <span class="label label-warning">activation</span>
        <div class="text-nowrap">Дата\n1 января 2020</div>
        <small class="user-badges"><span class="label label-success">поддержка</span>
        <span class="label label-success">арбитраж</span>
        <span class="label label-success">модерация</span></small>
        <div class="rating-full-count">123</div><span class="big">45</span></body>'''
        account.method = Mock(return_value=SimpleNamespace(content=html.encode()))
        profile = account.get_user(7)
        self.assertEqual(profile.username, 'seller')
        self.assertTrue(profile.online)
        self.assertTrue(profile.activation)
        self.assertTrue(profile.support and profile.arbitration and profile.moderation)
        self.assertEqual(profile.reg_data, '1 января 2020')
        self.assertEqual((profile.rating, profile.reviews, profile.lots_count), ('123', '45', 0))

    def test_order_keeps_aliases_and_upstream_fields(self):
        fields = {
            'summary': types.LotField('summary', {'ru': 'Название', 'en': 'Title'}),
            'desc': types.LotField('desc', {'ru': 'Описание'}),
            'payment_msg': types.LotField('payment_msg', {'ru': 'Спасибо'}),
            'level': types.LotField('level', '20', 'Уровень'),
        }
        order = types.Order('#ABC', OrderStatuses.PAID, None, None, None, fields,
                            2, 100, Currency.RUB, 'Player', 1, 'buyer', 2, 'seller',
                            3, None, [], 'ru')
        self.assertEqual((order.price, order.sum), (100, 100))
        self.assertEqual((order.description, order.title), ('Название', 'Название'))
        self.assertEqual(order.payment_msg, 'Спасибо')
        self.assertEqual(order.character_name, 'Player')
        order.buyer_params['Имя персонажа'] = 'CustomPlayer'
        self.assertEqual(order.character_name, 'CustomPlayer')
        self.assertEqual(order.lot_params_dict, {'Уровень': '20'})
        self.assertEqual(types.Server(7, 'Server').name, 'Server')
        self.assertEqual(types.Side(8, 'Side').id, 8)

    def test_auto_delivery_uses_most_specific_matching_section(self):
        config = configparser.ConfigParser()
        config.read_dict({'Game': {'response': 'generic'}, 'Game Premium': {'response': 'premium'}})
        cardinal = SimpleNamespace(AD_CFG=config, profile=SimpleNamespace(get_sorted_lots=lambda _: {}))
        event = SimpleNamespace(order=SimpleNamespace(description='Game Premium, buyer data', subcategory=None))
        handlers.setup_event_attributes_handler(cardinal, event)
        self.assertEqual(event.config_section_name, 'Game Premium')

    def test_auto_delivery_preserves_exact_match_priority(self):
        config = configparser.ConfigParser()
        config.read_dict({'Game Premium': {}, 'Game Premium, buyer data': {}})
        cardinal = SimpleNamespace(AD_CFG=config, profile=SimpleNamespace(get_sorted_lots=lambda _: {}))
        event = SimpleNamespace(order=SimpleNamespace(description='Game Premium, buyer data', subcategory=None))
        handlers.setup_event_attributes_handler(cardinal, event)
        self.assertEqual(event.config_section_name, 'Game Premium, buyer data')

    def test_auto_delivery_matches_server_and_side_and_retains_lot_id(self):
        lot = SimpleNamespace(id=77, server='Europe', side='Alliance', description='Gold')
        config = configparser.ConfigParser()
        config.read_dict({'Europe, Alliance, Gold': {'response': 'goods'}})
        cardinal = SimpleNamespace(AD_CFG=config, profile=SimpleNamespace(get_sorted_lots=lambda _: {None: {77: lot}}))
        event = SimpleNamespace(order=SimpleNamespace(description='Europe, Alliance, Gold, 10 units', subcategory=None))
        handlers.setup_event_attributes_handler(cardinal, event)
        self.assertEqual(event.lot_id, 77)
        self.assertIs(event.lot_shortcut, lot)

    def test_lot_fields_count_secrets_and_keep_database_inactive_state(self):
        lot = types.LotFields(7, {'auto_delivery': 'on', 'secrets': 'one\ntwo', 'active': 'on'}, db_amount=0)
        self.assertEqual(lot.amount, 2)
        self.assertFalse(lot.active)
        self.assertNotIn('amount', lot.renew_fields().fields)
        self.assertNotIn('deactivate_after_sale', lot.fields)

    def test_product_file_cannot_deliver_same_item_twice(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / 'products.txt'
            path.write_text('\n'.join(f'item-{i}' for i in range(40)))
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(lambda _: cardinal_tools.get_products(str(path)), range(40)))
            delivered = [result[0][0] for result in results]
            self.assertEqual(len(set(delivered)), 40)
            self.assertEqual(cardinal_tools.count_products(str(path)), 0)

    def test_proxy_dns_is_resolved_through_socks_proxy(self):
        parsed = cardinal_tools.validate_proxy('socks5://user:pass@127.0.0.1:1080')
        self.assertEqual(cardinal_tools.build_proxy(*parsed), 'socks5h://user:pass@127.0.0.1:1080')

    def test_chat_text_removes_invisible_suffix(self):
        self.assertEqual(strip_invisible_suffix('hello\u200b\u200c \n'), 'hello')
        self.assertEqual(strip_invisible_suffix('he\u200bllo'), 'he\u200bllo')
        self.assertEqual(parse_currency('RUB'), Currency.RUB)
        self.assertEqual(parse_currency('$'), Currency.USD)

    def test_uploader_registers_without_removed_backup_handler(self):
        telegram = Mock()
        file_uploader.init_uploader(SimpleNamespace(telegram=telegram))
        self.assertTrue(telegram.file_handler.called)
        for call in telegram.file_handler.call_args_list:
            self.assertTrue(callable(call.args[1]))
            self.assertNotEqual(call.args[0], 'upload_backup')

    def test_telegram_handlers_register_without_removed_methods(self):
        telegram = TGBot.__new__(TGBot)
        telegram.mdw_handler = Mock()
        telegram.cbq_handler = Mock()
        telegram.msg_handler = Mock()
        telegram._TGBot__register_handlers()
        self.assertGreater(telegram.msg_handler.call_count, 20)

    def test_sales_rejects_wrong_page_instead_of_emptying_order_list(self):
        account = Account('test')
        account._Account__initiated = True
        response = requests.Response()
        response.status_code = 200
        response._content = b'<div class="user-link-name">seller</div><h1>Wrong page</h1>'
        response.request = requests.Request('GET', 'https://funpay.com/orders/trade').prepare()
        account.method = Mock(return_value=response)
        with self.assertRaises(UnauthorizedError):
            account.get_sales()

    def test_fork_ui_does_not_restore_ads_or_upstream_self_update(self):
        self.assertFalse(hasattr(TGBot, 'edit_bot'))
        self.assertFalse(hasattr(TGBot, 'update'))
        self.assertFalse(hasattr(TGBot, 'send_announcements_kb'))
        keyboard = static_keyboards.UPLOAD_PLUGIN().to_dict()
        self.assertFalse(any('url' in button for row in keyboard['inline_keyboard'] for button in row))
        links = keyboards.links().to_dict()['inline_keyboard']
        self.assertEqual(links[0][0]['url'], 'https://github.com/chtowsappx/FunPayCardinal')

    def test_legacy_proxy_config_migration_retains_credentials(self):
        with tempfile.TemporaryDirectory() as directory:
            config = configparser.ConfigParser(delimiters=(":",))
            config.optionxform = str
            config.read_dict(first_setup.default_config)
            config['FunPay']['golden_key'] = 'test'
            config['Proxy'].pop('proxy')
            config['Proxy'].update({'ip': '127.0.0.1', 'port': '8080', 'login': 'user', 'password': 'pass'})
            path = pathlib.Path(directory) / 'main.cfg'
            with path.open('w') as file:
                config.write(file)
            real_open = open
            with patch('builtins.open', create=True, wraps=real_open) as opener:
                def redirected(filename, *args, **kwargs):
                    if filename == 'configs/_main.cfg':
                        filename = pathlib.Path(directory) / 'migrated.cfg'
                    return real_open(filename, *args, **kwargs)
                opener.side_effect = redirected
                loaded = config_loader.load_main_config(str(path))
            self.assertEqual(loaded['Proxy']['proxy'], 'http://user:pass@127.0.0.1:8080')
            self.assertNotIn('password', loaded['Proxy'])


if __name__ == '__main__':
    unittest.main()

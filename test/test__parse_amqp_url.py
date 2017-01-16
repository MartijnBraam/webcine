from unittest import TestCase

import webcine.utils.queue


class Test_parse_amqp_url(TestCase):
    def test__parse_amqp_url(self):
        url = 'amqp://localhost'
        result = webcine.utils.queue._parse_amqp_url(url)
        self.assertTupleEqual(result, ('localhost', 5672, '', None))

        url = 'localhost'
        result = webcine.utils.queue._parse_amqp_url(url)
        self.assertTupleEqual(result, ('localhost', 5672, '', None))

        url = 'amqp://localhost/webcine'
        result = webcine.utils.queue._parse_amqp_url(url)
        self.assertTupleEqual(result, ('localhost', 5672, '/webcine', None))

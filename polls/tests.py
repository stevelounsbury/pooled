import datetime
import unittest
from models import Poll, Choice

class PollTest(unittest.TestCase):
    def setUp(self):
        self.p = Poll(question="Yo yo!", pub_date=datetime.datetime.now())
        self.p.save()

    def testPublishedToday(self):
        self.assertTrue(self.p.was_published_today())

    def testFindByStartsWith(self):
        tp = Poll.objects.filter(question__startswith='Yo')
        self.assertEquals(tp.count(), 1) 

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from backend import queue

class SimpleTest(TestCase):
#     def test_basic_addition(self):
#         """
#         Tests that 1 + 1 always equals 2.
#         """
#         self.assertEqual(1 + 1, 2)
    
    def test_sms2send(self):
        r = queue.sms2send.delay(data={"sms_id":3486})
        self.assertEqual(r.status, 'SUCCESS')
     
    def test_sms2gate(self):
        r = queue.sms2gate.delay(data={"id":3209})
        self.assertEqual(r.status, 'SUCCESS')
        
    def test_notice2staff(self):
        data = {}
        data['staff_id'] = 1555
        data['unread_mentors'] = 5
        data['unread_waiters'] = 10
        r = queue.notice2staff.delay(data)
        self.assertEqual(r.status, 'SUCCESS')
        
    def test_apns(self):
        data = {}
        data['token'] = ''
        data['alert'] = ''
        data['badge'] = ''
        data['sound'] = ''
        r = queue.apns.delay(data)
        self.assertEqual(r.status, 'SUCCESS')


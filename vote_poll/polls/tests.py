import datetime

from django.utils import timezone
from django.test import TestCase
from django.core.urlresolvers import reverse
from polls.models import Poll

class PollMethodTests(TestCase):

    def test_was_published_recently_with_future_poll(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_poll = Poll(pub_date=time)
        self.assertEqual(future_poll.was_published_recently(), False)

    def test_was_published_recently_with_old_poll(self):
        time = timezone.now() - datetime.timedelta(days=30)
        old_poll = Poll(pub_date=time)
        self.assertEqual(old_poll.was_published_recently(), False)

    def test_was_published_recently_with_recent_poll(self):
        time = timezone.now() - datetime.timedelta(hours=1)
        recent_poll = Poll(pub_date=time)
        self.assertEqual(recent_poll.was_published_recently(), True)

def create_poll(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Poll.objects.create(question=question,
                                   pub_date=time)

class PollViewTests(TestCase):

    def test_index_view_with_no_poll(self):
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])

    def test_index_view_with_a_past_poll(self):
        create_poll(question="Past poll.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_poll_list'],
            ['<Poll: Past question.>']
        )

    def test_index_view_with_a_future_poll(self):
        create_poll(question="Future poll.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.",
                            status_code=200)
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])

    def test_index_view_with_future_poll_and_past_poll(self):
        create_poll(question="Past poll.", days=-30)
        create_poll(question="Future poll.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_poll_list'],
            ['<Poll: Past poll.>']
        )

    def test_index_view_with_two_past_poll(self):
        create_poll(question="Past poll 1.", days=-30)
        create_poll(question="Past poll 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_poll_list'],
            ['<Poll: Past poll 2.>', '<Poll: Past poll 1.>']
        )

class PollIndexDetailTests(TestCase):
    def test_detail_view_with_a_future_poll(self):
        future_poll = create_poll(question='Future poll.',
                                          days=5)
        response = self.client.get(reverse('polls:detail',
                                   args=(future_poll.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_poll(self):
        past_poll = create_poll(question='Past poll.',
                                        days=-5)
        response = self.client.get(reverse('polls:detail',
                                   args=(past_poll.id,)))
        self.assertContains(response, past_poll.question,
                            status_code=200)
from django.test import TestCase
import datetime
from django.utils import timezone
from django.test import TestCase
from .models import Question, Choice
from django.core.urlresolvers import reverse

# Create your tests here.


class QuestionMethodTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() should return False for questions whose
        pub_date is in the future.
        """

        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertEqual(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() should return False for questions whose
        pub_date is older than 1 day.
        """

        time = timezone.now() - datetime.timedelta(days=30)
        old_question = Question(pub_date=time)
        self.assertEqual(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() should return False for questions whose
        pub_date is within last day.
        """

        time = timezone.now() - datetime.timedelta(hours=1)
        recent_question = Question(pub_date=time)
        self.assertEqual(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """
    Create a question with the given 'question_text' and published  the given number
    of 'days' offset to now (negetive for questions published in the past)
    :param question_text:
    :param days:
    :return:
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


def create_choice(question, choices_text):
    return Choice.objects.create(question=question, choices_text=choices_text)


class QuestionViewTests(TestCase):
    def test_index_view_with_no_question(self):
        """
        if no question exist, an appropriate message should be displayed.
        :return:
        """
        response = self.client.get(reverse('pools:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No pools are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_a_past_question(self):
        """
        Questions with a pub_date in the past should be displayed on the index page
        :return:
        """
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('pools:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_indext_view_with_a_future_question(self):
        """
        Questions with a pub_date in the future should not be displayed on the index pageg.
        :return:
        """

        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('pools:index'))
        self.assertContains(response, "No pools are available.", status_code=200)
        self.assertQuerysetEqual(
                response.context['latest_question_list'], []
        )

    def test_index_view_with_future_question_and_past_question(self):
        """
        Even if both past and future question exist, only past question should be display
        :return:
        """

        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('pools:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'], ['<Question: Past question.>']
        )

    def test_index_view_with_tow_past_questions(self):
        """
        The questions index page may display multiple questions.
        :return:
        """
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('pools:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )

    def test_index_view_with_question_has_no_choice(self):
        """
        The question with no choice shouldn't be listed
        :return:
        """
        create_question(question_text="questions with no choice.", days=-5)
        response = self.client.get(reverse('pools:index'))
        self.assertContains(response, "No pools are available.", status_code=200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_question_has_several_choice(self):
        """
        The question with no choice should be list
        :return:
        """
        question = create_question(question_text="question1 with 2 choice.", days=-5)
        create_choice(question, "choice 1 of question1")
        create_choice(question, "choice 2 of question1")
        response = self.client.get(reverse('pools:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question>: question1 with 2 choice']
        )


class QuestionIndexDetailTests(TestCase):
    def test_detail_view_with_a_future_question(self):
        """
        The detail view of a question with a pub_date in the future should return a
        404 not found
        :return:
        """

        future_question = create_question(question_text='Future question.', days=30)
        response = self.client.get(reverse('pools:detail', args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_a_past_question(self):
        """
        The detail view of a question with a pub_date in the past should display the
        question's text
        :return:
        """

        past_question = create_question(question_text='past question.', days=-10)
        response = self.client.get(reverse('pools:detail', args=(past_question.id, )))
        self.assertContains(response, "past question.", status_code=200)
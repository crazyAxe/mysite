from django.shortcuts import render

# Create your views here.
from .models import Question, Choice
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.views import generic


class IndexView(generic.ListView):
    template_name = 'pools/index.html'
    context_object_name = 'latest_question_list'
    #
    # def get_queryset(self):
    #     """
    #      Return the last five published questions.(not include those set to
    #     be published in the future).
    #     """
    #     return Question.objects.filter(
    #         pub_date__lte=timezone.now()
    #     ).order_by('-pub_date')

    def get_queryset(self):
        """
        Only show questions which have choices, exclude that questions with no question.
        :return:
        """
        questions = Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')
        questions_show = [questions[i] for i in range(0, len(questions)) if questions[i].choice_set.all()]
        return questions_show


class DetailView(generic.DetailView):
    model = Question
    template_name = 'pools/detail.html'

    def get_queryset(self):
        """
        Excludes any question that aren't published yet.
        :return:
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'pools/results.html'

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())

# def index(request):
#     latest_question_list = Question.objects.order_by('-pub_date')[:5]
#     context = {'latest_question_list': latest_question_list}
#     return render(request, 'pools/index.html', context)

# def index(request):
#     latest_question_list = Question.objects.order_by('-pub_date')
#     template = loader.get_template('pools/index.html')
#     context = {
#         'latest_question_list': latest_question_list,
#     }
#     output = ', '.join([q.question_text for q in latest_question_list])
#     return HttpResponse(template.render(context, request))


# def detail(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'pools/detail.html', {'question': question})


# def detail(request, question_id):
#     try:
#         question = Question.objects.get(pk=question_id)
#     except Question.DoesNotExist:
#         raise Http404("Question does not exist")
#     return render(request, 'pools/detail.html', {'question': question})


# def results_(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'pools/results.html', context={'question': question})


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        select_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'pools/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice",
        })
    else:
        select_choice.votes += 1
        select_choice.save()
        return HttpResponseRedirect(reverse('pools:results', args=(question.id,)))
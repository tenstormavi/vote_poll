from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone

from polls.models import Choice, Poll


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_poll_list'

    def get_queryset(self):
        return Poll.objects.filter(
        pub_date__lte=timezone.now()
    ).order_by('-pub_date')[:5]

def home(request):
    return render(request, 'polls/home.html')


class DetailView(generic.DetailView):
    model = Poll
    template_name = 'polls/detail.html'
    
    def get_queryset(self):
        return Poll.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Poll
    template_name = 'polls/results.html'


def vote(request, poll_id):
    p = get_object_or_404(Poll, pk=poll_id)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the poll voting form.
        return render_to_response('polls/detail.html', {
            'poll': p,
            'error_message': "You didn't select a choice.",
        }, context_instance=RequestContext(request))
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(p.id,)))

def add(request, poll_id):
    p = get_object_or_404(Poll, pk = poll_id)

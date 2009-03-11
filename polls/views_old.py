from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse

from testsite.polls.models import Poll, Choice
# Create your views here.

def index(request):
    poll_list = Poll.objects.all().order_by('-pub_date')[:5] 
    t = loader.get_template('polls/index.html')
    c = Context({
        'poll_list': poll_list
    })
    return HttpResponse(t.render(c))

def detail(request, object_id):
    try:
        p = Poll.objects.get(pk=object_id)
    except Poll.DoesNotExist:
        raise Http404
    return render_to_response('polls/detail.html', {'poll': p})

def vote(request, poll_id):
    p = get_object_or_404(Poll, pk=poll_id)

    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render_to_response('polls/poll_detail.html', {
            'poll': p,
            'error_message': 'You fucked up',
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()

        return HttpResponseRedirect(reverse('poll_results', args=(p.id,)))

def results(request, object_id):
    p = get_object_or_404(Poll, pk=object_id)
    return render_to_response('poll_results', {'poll': p})

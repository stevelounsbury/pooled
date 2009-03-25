from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.views import login
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    return render_to_response('pooled/index.html', context_instance=RequestContext(request))
import json

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse

from aggregate.client import get_client

@user_passes_test(lambda u:u.is_superuser)
def global_stats(request):
    stats = get_client().select(group_by=['query'], where={'type':'sql'})
    for s in stats:
        s['average_time'] = s['time'] / s['count']
    return render(request, 'profiler/index.html', {'queries' : stats})

@user_passes_test(lambda u:u.is_superuser)
def global_stats_mongo(request):
    stats = get_client().select(group_by=['query'], where={'type':'mongo'})
    for s in stats:
        s['average_time'] = s['time'] / s['count']
    return render(request, 'profiler/index.html', {'queries' : stats})

@user_passes_test(lambda u:u.is_superuser)
def stats_by_view(request):
    stats = get_client().select(group_by=['view','query'], where={'type':'sql'})
    return _render_stats(stats)

@user_passes_test(lambda u:u.is_superuser)
def mongo_stats_by_view(request):
    stats = get_client().select(group_by=['view','query'], where={'type':'mongo'})
    return _render_stats(stats)

@user_passes_test(lambda u:u.is_superuser)
def reset(request):
    next = request.GET.get('next') or request.POST.get('next') or request.META.get('HTTP_REFERER') or reverse('profiler_global_stats')
    if request.method == 'POST':
        get_client().clear()
        return HttpResponseRedirect(next)
    return render(request, 'profiler/reset.html', {'next' : next})

@user_passes_test(lambda u:u.is_superuser)
def python_stats(request):
    stats = get_client().select(group_by=['file','lineno'], where={'type':'python'})
    return render(request, 'profiler/code.html', {'stats' : stats})

def _render_stats(stats):
    grouped = {}
    for r in stats:
        if r['view'] not in grouped:
            grouped[r['view']] = {'queries' : [], 
                                  'count' : 0,
                                  'time' : 0,
                                  'average_time' : 0}
        grouped[r['view']]['queries'].append(r)
        grouped[r['view']]['count'] += r['count']
        grouped[r['view']]['time'] += r['time']
        r['average_time'] = r['time'] / r['count'] 
        grouped[r['view']]['average_time'] += r['average_time']
        
    maxtime = 0
    for r in stats:
        if r['average_time'] > maxtime:
            maxtime = r['average_time']
    for r in stats:
        r['normtime'] = (0.0+r['average_time'])/maxtime
           
    return render(request, 'profiler/by_view.html', {'queries' : grouped, 'stats' :json.dumps(stats)})

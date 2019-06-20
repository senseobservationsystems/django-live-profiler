import inspect

import statprof

from django.conf import settings
from django.urls import resolve

from aggregate.client import get_client

from profiler import _set_current_view


def ProfilerMiddleware(get_response):
    def middleware(request):
        if request.path.startswith('/profiler'):
            return get_response(request)

        view = resolve(request.path).func
        if inspect.ismethod(view):
            view_name = view.__class__.__module__+ '.' + view.__class__.__name__
        else:
            view_name = view.__module__ + '.' + view.__name__
        
        _set_current_view(view_name)

        return get_response(request)

    return middleware



def StatProfMiddleware(get_response):
    def middleware(request):
        if request.path.startswith('/profiler'):
            return get_response(request)

        # print(f'[i] Starting sampling on {request.path}..')
        statprof.reset(getattr(settings, 'LIVEPROFILER_STATPROF_FREQUENCY', 100))
        statprof.start()
    
        response = get_response(request)

        statprof.stop()
        total_samples = statprof.state.sample_count
        if total_samples == 0:
            return response
        secs_per_sample = statprof.state.accumulated_time / total_samples

        # print('[i] Getting ZQM client...')
        client = get_client()
        client.insert_all([
            (
                {
                    'file': c.key.filename,
                    'lineno': c.key.lineno,
                    'function': c.key.name,
                    'type': 'python',
                },
                {
                    'self_nsamples': c.self_sample_count,
                    'cum_nsamples': c.cum_sample_count,
                    'tot_nsamples': total_samples,
                    'cum_time': c.cum_sample_count * secs_per_sample,
                    'self_time': c.self_sample_count * secs_per_sample,
                }
            )
            for c in statprof.CallData.all_calls.values()
        ])
        # print(f'[i] Saved {statprof.state.sample_count} samples for {request.path}.')

        return response

    return middleware

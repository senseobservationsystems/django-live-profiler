====================
django-live-profiler
====================

Django-live-profiler is a low-overhead data access and code profiler for Django-based applications. For more information, check out http://invitebox.github.com/django-live-profiler/

------------
Installation
------------
1. Run `pip install django-live-profiler`
2. Add `'profiler'` app to `INSTALLED_APPS` 
3. Add `'profiler.middleware.ProfilerMiddleware'` to `MIDDLEWARE`
4. Optionally add `'profiler.middleware.StatProfMiddleware'` to `MIDDLEWARE` to enable Python code statistical profiling (using statprof_). WARNING: this is an experimental feature, beware of possible incorrect output.
5. Add `url(r'^profiler/', include('profiler.urls'))` to your urlconf

.. _statprof: https://github.com/bos/statprof.py

-----
Usage
-----

In order to start gathering data you need to start the aggregation server::

  $ aggregated --host 127.0.0.1 --port 5556

Note, you must run Django with threading disabled in order for statprof to work!

  $ ./manage runserver --noreload --nothreading

You may experience issues with staticfiles loading in chrome when `--nothreading` is passed.

This is because chrome opens two initial connections, which blocks when Django is only able to respond to one of them.  To fix this, you must serve staticfiles via separate staticfile server, such as nginx with a reverse_proxy to your Django runserver.

Visit http://yoursite.com/profiler/ for results.


Note: you must be logged in as a superuser to view the profiler page.
You can create a superuser account with:

  $ ./manage.py createsuperuser

from django.urls import path

from .views import (
    global_stats,
    global_stats_mongo,
    stats_by_view,
    mongo_stats_by_view,
    python_stats,
    reset,
)

urlpatterns = [
    path('', global_stats, name='profiler_global_stats'),
    path('mongo/', global_stats_mongo, name='profiler_global_stats_mongo'),
    path('by_view/', stats_by_view, name='profiler_stats_by_view'),
    path('by_view/mongo/', mongo_stats_by_view, name='profiler_mongo_stats_by_view'),
    path('code/', python_stats, name='profiler_python_stats'),
    path('reset/', reset, name='profiler_reset'),
]


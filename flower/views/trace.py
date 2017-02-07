from __future__ import absolute_import

import logging

from tornado import web
from tornado import gen

from ..views import BaseHandler
from ..api.workers import ListWorkers
from ..tracer.data_collector import DataTracer, Patttern


logger = logging.getLogger(__name__)


class TraceView(BaseHandler):
    @web.authenticated
    def get(self):
        app = self.application
        capp = self.application.capp

        self.render(
            "filtered_tasks.html",
            ftasks = [],
            provider_name = None,
            task_name = None,
            task_date = None,
            task_hour = None,
            cursor = 0
        )


class FilteredTasksView(BaseHandler):
    @web.authenticated
    def get(self):
        app = self.application
        capp = self.application.capp

        provider_name = self.get_argument('p_name', type=str) 
        task_name = self.get_argument('t_name', type=str)
        task_date = self.get_argument('t_date', type=str)        
        task_hour = self.get_argument('hour', type=str)
        cursor_pos = self.get_argument('cursor', type=str)

        if cursor_pos is None:
            cursor_pos = 0

        pattern = Patttern(provider_name, task_name, task_date)
        key = pattern.get_redis_key_pattern()

        cursor_pos, matched_tasks = DataTracer.get_all_data_for_pattern(cursor_pos, key)
        # matched_tasks = DataTracer.get_all_data_for_pattern_iter(key)
        sorted_tasks = DataTracer.sort_on_processed_time(matched_tasks)

        self.render(
            "filtered_tasks.html",
            ftasks = sorted_tasks,
            provider_name = provider_name,
            task_name = task_name,
            task_date = task_date,
            task_hour = task_hour,
            cursor = cursor_pos
        )

class TracedTasksView(BaseHandler):
    @web.authenticated
    def get(self, task_id):
        task_obj = DataTracer.get_task_by_id(task_id)

        self.render(
            "traced_task.html",
            task = task_obj
        )
# encoding=utf-8
# created @2024/12/11
# created by zhanzq
#

import os
from sanic.views import HTTPMethodView
from sanic import html
from utils import load_template
from jinja2 import Template
from haier_auto_test import HaierAutoTest


auto_test = HaierAutoTest(
    env="test",
    device="X20",
    service_type="dm",
    block_info_check=False,
    tpl_match_check=False,
    do_nlu_check=False,
    log_trace_check=False,
    do_nlp_analysis_check=True
)


# View to handle rendering and form submission
class LogAnalysisView(HTTPMethodView):
    async def get(self, request):
        log_analysis_template = os.path.join(os.path.dirname(__file__), "../templates/log_analysis.html")
        template = load_template(template_path=log_analysis_template)
        print(auto_test)
        return html(Template(template).render(
            environment=auto_test.env,
            service_type=auto_test.service_type,
            device=auto_test.device,
            user_query="",
            block_info=auto_test.block_info_check,
            tpl_match=auto_test.tpl_match_check,
            do_nlu=auto_test.do_nlu_check,
            log_trace=auto_test.log_trace_check,
            doNlpAnalysis=auto_test.do_nlp_analysis_check,
            log_output=""
        ))

    async def post(self, request):
        form_data = request.form
        auto_test.env = form_data.get('environment', auto_test.env)
        auto_test.service_type = form_data.get('service_type', auto_test.service_type)
        auto_test.device = form_data.get('device', auto_test.device)
        auto_test.block_info_check = 'block_info' in form_data.getlist("log_option")
        auto_test.tpl_match_check = 'tpl_match' in form_data.getlist("log_option")
        auto_test.do_nlu_check = 'do_nlu' in form_data.getlist("log_option")
        auto_test.log_trace_check = 'log_trace' in form_data.getlist("log_option")
        auto_test.do_nlp_analysis_check = 'doNlpAnalysis' in form_data.getlist("log_option")

        user_query = form_data.get('user_query', '').strip()
        action = form_data.get('action', '')

        if user_query:
            if action == 'test':
                log_output = auto_test.process_input(input_text=user_query)
            elif action == 'bug':
                log_output = auto_test.bug_reproduce(sn=user_query)
        else:
            log_output = ""

        log_analysis_template = os.path.join(os.path.dirname(__file__), "../templates/log_analysis.html")
        template = load_template(template_path=log_analysis_template)
        return html(Template(template).render(
            environment=auto_test.env,
            service_type=auto_test.service_type,
            device=auto_test.device,
            user_query=user_query,
            block_info=auto_test.block_info_check,
            tpl_match=auto_test.tpl_match_check,
            do_nlu=auto_test.do_nlu_check,
            log_trace=auto_test.log_trace_check,
            doNlpAnalysis=auto_test.do_nlp_analysis_check,
            log_output=log_output
        ))

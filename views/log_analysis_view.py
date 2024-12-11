# encoding=utf-8
# created @2024/12/11
# created by zhanzq
#

import os
from sanic.views import HTTPMethodView
from sanic import html
from utils import load_template
from jinja2 import Template


# Default values for the form
DEFAULTS = {
    'environment': 'dev',
    'service_type': 'dm',
    'device': 'Television',
    'block_info': False,
    'tpl_match': False,
    'do_nlu': False,
    'log_trace': False,
    'doNlpAnalysis': True
}


# View to handle rendering and form submission
class LogAnalysisView(HTTPMethodView):
    async def get(self, request):
        log_analysis_template = os.path.join(os.path.dirname(__file__), "../templates/log_analysis.html")
        template = load_template(template_path=log_analysis_template)
        print(DEFAULTS)
        return html(Template(template).render(
            environment=DEFAULTS['environment'],
            service_type=DEFAULTS['service_type'],
            device=DEFAULTS['device'],
            user_query="",
            block_info=DEFAULTS['block_info'],
            tpl_match=DEFAULTS['tpl_match'],
            do_nlu=DEFAULTS['do_nlu'],
            log_trace=DEFAULTS['log_trace'],
            doNlpAnalysis=DEFAULTS['doNlpAnalysis'],
            log_output=""
        ))

    async def post(self, request):
        form_data = request.form
        environment = form_data.get('environment', [DEFAULTS['environment']])
        service_type = form_data.get('service_type', [DEFAULTS['service_type']])
        device = form_data.get('device', [DEFAULTS['device']])
        user_query = form_data.get('user_query', '')

        block_info = 'block_info' in form_data.getlist("log_option")
        tpl_match = 'tpl_match' in form_data.getlist("log_option")
        do_nlu = 'do_nlu' in form_data.getlist("log_option")
        log_trace = 'log_trace' in form_data.getlist("log_option")
        doNlpAnalysis = 'doNlpAnalysis' in form_data.getlist("log_option")

        log_output = f"Query: {user_query}\nEnvironment: {environment}\nService: {service_type}\nDevice: {device}\n"
        log_output += f"block_info: {block_info}\ntpl_match: {tpl_match}\ndo_nlu: {do_nlu}\n"
        log_output += f"log_trace: {log_trace}\ndoNlpAnalysis: {doNlpAnalysis}"

        action = form_data.get('action', '')
        if action == 'test':
            log_output += "\nAction: Test clicked"
        elif action == 'bug':
            log_output += "\nAction: Bug Reproduce clicked"

        # update DEFAULTS config
        DEFAULTS["environment"] = environment
        DEFAULTS["service_type"] = service_type
        DEFAULTS["device"] = device
        DEFAULTS["block_info"] = block_info
        DEFAULTS["tpl_match"] = tpl_match
        DEFAULTS["do_nlu"] = do_nlu
        DEFAULTS["log_trace"] = log_trace
        DEFAULTS["doNlpAnalysis"] = doNlpAnalysis

        log_analysis_template = os.path.join(os.path.dirname(__file__), "../templates/log_analysis.html")
        template = load_template(template_path=log_analysis_template)
        return html(Template(template).render(
            environment=environment,
            service_type=service_type,
            device=device,
            user_query=user_query,
            block_info=block_info,
            tpl_match=tpl_match,
            do_nlu=do_nlu,
            log_trace=log_trace,
            doNlpAnalysis=doNlpAnalysis,
            log_output=log_output
        ))

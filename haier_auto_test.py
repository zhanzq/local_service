# encoding=utf-8
# created @2024/12/12
# created by zhanzq
#
import json
import requests
from common_utils import format_string
from common_utils.haier.auto_test.parse_log import LogParser
from common_utils.haier.auto_test.nlu import NLU


class HaierAutoTest:
    def __init__(self,
                 env="test",
                 device="X20",
                 service_type="dm",
                 block_info_check=False,
                 tpl_match_check=False,
                 do_nlu_check=False,
                 log_trace_check=False,
                 do_nlp_analysis_check=False):
        self.parser = NLU()
        self.log_parser = LogParser(env=env)
        self.device = device
        self.env = env
        self.service_type = service_type
        self.block_info_check = block_info_check
        self.tpl_match_check = tpl_match_check
        self.do_nlu_check = do_nlu_check
        self.log_trace_check = log_trace_check
        self.do_nlp_analysis_check = do_nlp_analysis_check
        pass

    def bug_reproduce(self, sn):
        self.log_parser.update_config(env=self.env, sn=sn)
        service_name = "dialog-system:doNlu"
        resp_obj = self.log_parser.get_service_info(service_name=service_name)
        req = resp_obj.get("data").get("reqBody")
        args = json.loads(req)

        post_json = args.get("args0", {})
        post_json.pop("sn", None)
        post_json["userId"] = "bug_produce_0001"
        url = {
            "service": "https://aiservice.haier.net/dialog-system/v2/dialog",
            "sim": "https://aisim.haiersmarthomes.com/dialog-system/v2/dialog",
            "test": "https://aitest.haiersmarthomes.com/dialog-system/v2/dialog"
        }[self.env]
        payload = json.dumps(post_json)
        headers = {
            "Content-Type": "application/json",
            "auth": "access_nlp_12345678"
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        resp_json = json.loads(response.text)
        out = json.dumps(resp_json, indent=4, ensure_ascii=False)

        return out

    def process_input(self, input_text):
        # Get the input text
        if self.service_type == "dm":
            return self.dm(input_text, simulation=True)
        elif self.service_type == "nlu":
            return self.nlu(input_text)
        elif self.service_type == "template":
            return self.template(input_text)
        elif self.service_type == "extract_log":
            return self.extract_log(input_text)
        else:
            return ""

    def dm(self, text, simulation=True):
        query_lst = text.split("\n")
        out = []
        for i, query in enumerate(query_lst):
            query = query.strip()
            print(f"query: {query}")
            case = format_string(f"case {i + 1:03d}", length=80)
            out.append(case)
            json_resp = self.parser.get_dm_service_response(query=query, env=self.env, device=self.device, simulation=simulation)
            dm_info = self.parser.parse_dm_response(json_resp=json_resp)
            formatted = json.dumps(dm_info, indent=4, ensure_ascii=False)
            out.append(formatted)

        return "\n".join(out)

    def nlu(self, text):
        query_lst = text.split("\n")
        out = []
        for i, query in enumerate(query_lst):
            query = query.strip()
            print(f"query: {query}")
            case = format_string(f"case {i + 1:03d}", length=80)
            out.append(case)
            json_resp = self.parser.get_nlu_service_response(query=query, env=self.env, device=self.device)
            nlu_info = self.parser.parse_nlu_response(json_resp=json_resp)
            formatted = json.dumps(nlu_info, indent=4, ensure_ascii=False)
            out.append(formatted)
            # time.sleep(0.2)

        return "\n".join(out)

    def template(self, text):
        query_lst = text.split("\n")
        out = []
        for i, query in enumerate(query_lst):
            query = query.strip()
            case = format_string(f"case {i + 1:03d}: {query}", length=80)
            out.append(case)
            json_resp = self.parser.get_tpl_service_response(query=query)
            tpl_info = self.parser.parse_tpl_response(json_resp=json_resp)
            formatted = json.dumps(tpl_info, indent=4, ensure_ascii=False)
            out.append(formatted)

        return "\n".join(out)

    @staticmethod
    def replace_control_chars(text):
        text = text.replace("\\n\\r", "\n").replace("\\n", "\n").replace("\\t", "\t")
        return text

    def extract_log(self, text, block_domain_check=None):
        self.log_parser.update_config(env=self.env)
        block_info_check = self.block_info_check
        tpl_match_check = self.tpl_match_check
        do_nlu_check = self.do_nlu_check
        log_trace_check = self.log_trace_check
        do_nlp_analysis_check = self.do_nlp_analysis_check
        sn_lst = text.split("\n")
        out = []
        for i, sn in enumerate(sn_lst):
            self.log_parser.update_config(sn=sn.strip())
            query = self.log_parser.get_query_by_sn()
            case = format_string(f"case {i + 1:03d}: {query}", length=80)
            out.append(case)

            if not block_domain_check:
                block_domain_check = ["Dev.Oven", "Steamer", "SteamBaker", "Lamp", "IntegratedStove", "Dev.cookHood"]

            if block_info_check:
                block_info = self.log_parser.block_check(domain_lst=block_domain_check, verbose=False)
                out.append(format_string("block_info", length=80))
                out.append(json.dumps(block_info, indent=4, ensure_ascii=False))

            if tpl_match_check:
                tpl_match_info = self.log_parser.get_tpl_match_info_from_log(verbose=False)
                out.append(format_string("tpl_match_info", length=80))
                out.append(json.dumps(tpl_match_info, indent=4, ensure_ascii=False))

            if do_nlu_check:
                do_nlu_info = self.log_parser.get_do_nlu_info_from_log(verbose=False)
                out.append(format_string("do_nlu_info", length=80))
                out.append(json.dumps(do_nlu_info, indent=4, ensure_ascii=False))

            if log_trace_check:
                log_trace_info = self.log_parser.get_log_trace_info_from_log(verbose=False)
                out.append(format_string("log_trace_info", length=80))
                out.append(log_trace_info)

            if do_nlp_analysis_check:
                nlp_analysis_info = self.log_parser.get_do_nlp_analysis_info_from_log(verbose=False)
                out.append(format_string("do_nlp_analysis", length=80))
                out.append(json.dumps(nlp_analysis_info, indent=4, ensure_ascii=False))

        return "\n".join(out)

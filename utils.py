# encoding=utf-8
# created @2024/12/10
# created by zhanzq
#

import socket


# Helper function to load the template
def load_template(template_path):
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


class PortInUseError(Exception):
    def __init__(self, message):
        self.message = message


def check_port_in_use(port, host="127.0.0.1"):
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.bind((host, int(port)))
    except socket.error:
        raise PortInUseError(f"端口：{port} 已被占用")
    finally:
        if s:
            s.close()

import os
from typing import Any

class EdgeObserve:
    def __init__(self, args):
        # must put define_img_size() before 'import create_mb_tiny_fd, create_mb_tiny_fd_predictor'
        ori_dir = os.getcwd()
        os.chdir(os.path.dirname(__file__) or '.')
        print('{}'.format(os.getcwd()))
        self.cache = args['cache']

        os.chdir(ori_dir)

    def __call__(self, input_ctx):
        output_ctx = {}
        if 'frame' not in input_ctx:
            # return empty due to no input_ctx
            return output_ctx
        frame, lps, rps = input_ctx["frame"], input_ctx["lps"], input_ctx["rps"]
        output_ctx["frame"] = frame
        output_ctx["lps"] = lps
        output_ctx["rps"] = rps
        return output_ctx

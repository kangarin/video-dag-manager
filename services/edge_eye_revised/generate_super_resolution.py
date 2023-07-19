import os
import util_ixpe

# 之前的ROI的高度只包含reference bar，但是宽度与原图像一样，这里进一步裁小
def extractMinimizedROI(bar_roi, lps, rps, abs_point):
    lps = int(lps - abs_point[0])
    rps = int(rps - abs_point[0])
    sliding_threshold = 10
    hl_threshold = 15
    height = bar_roi.shape[0]
    p1 = (lps - 3 * hl_threshold - sliding_threshold, 0)
    p2 = (lps + hl_threshold + sliding_threshold, height)
    p3 = (rps - hl_threshold - sliding_threshold, 0)
    p4 = (rps + 3 * hl_threshold + sliding_threshold, height)
    lroi = bar_roi[p1[1]:p2[1], p1[0]:p2[0]]
    rroi = bar_roi[p3[1]:p4[1], p3[0]:p4[0]]
    return lroi, rroi, p1, p3

class GenerateSuperResolution:
    def __init__(self, args):

        # must put define_img_size() before 'import create_mb_tiny_fd, create_mb_tiny_fd_predictor'
        ori_dir = os.getcwd()
        os.chdir(os.path.dirname(__file__) or '.')
        print('{}'.format(os.getcwd())) 
        self.sr_generator = util_ixpe.ESCPN()
        self.cache = args['cache']
        os.chdir(ori_dir)  

    def __call__(self, input_ctx):
        output_ctx = {}
        # if input_ctx does not contain 'frame'
        if 'frame' not in input_ctx:
            # case 1: return empty due to no input_ctx
            return output_ctx
        bar_roi, abs_point, frame = input_ctx["bar_roi"], input_ctx["abs_point"], input_ctx["frame"]
        lps, rps = self.cache.get_edge_position()
        
        if lps == 0 and rps == 0:
            output_ctx["bar_roi"] = bar_roi
            output_ctx["abs_point"] = abs_point
            output_ctx["frame"] = frame
            # case 2: return 3 parameters
            return output_ctx
        else:
            lroi, rroi, p1, p3 = extractMinimizedROI(
                bar_roi, lps, rps, abs_point)
            if lroi.size == 0 or rroi.size == 0:
                # case 3: return empty
                return output_ctx
            lhit_position = self.cache.cacher_hit('l', frame=lroi)
            rhit_position = self.cache.cacher_hit('r', frame=rroi)

            if lhit_position != -1 and rhit_position != -1:  # 尝试检查lroi是否cache命中xxx
                lps = p1[0] + lhit_position
                rps = p3[0] + rhit_position
                self.cache.set_edge_position([lps, rps])
                # case 4: return empty
                return output_ctx
            else:
                srl = self.sr_generator.genSR(lroi)
                self.cache.cacher_update('l', frame=lroi)
                srr = self.sr_generator.genSR(rroi)
                self.cache.cacher_update('r', frame=rroi)

                labs_point = (abs_point[0] + p1[0], abs_point[1] + p1[1])
                rabs_point = (abs_point[0] + p3[0], abs_point[1] + p3[1])
                output_ctx["srl"] = srl
                output_ctx["srr"] = srr
                output_ctx["labs_point"] = labs_point
                output_ctx["rabs_point"] = rabs_point
                output_ctx["frame"] = frame
                # case 5: return 5 parameters
                return output_ctx
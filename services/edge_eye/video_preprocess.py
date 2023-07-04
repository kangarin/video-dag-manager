import os
import util_ixpe

class VideoPreprocess:
    def __init__(self, args):

        # must put define_img_size() before 'import create_mb_tiny_fd, create_mb_tiny_fd_predictor'
        ori_dir = os.getcwd()
        os.chdir(os.path.dirname(__file__) or '.')
        print('{}'.format(os.getcwd())) 
        self.d_area = args['d_area']
        self.bar_area = args['bar_area'] 
        self.mat_detector = util_ixpe.MaterialDetection(
        detection_area=self.d_area, buffer_size=20)
        self.bar_selector = util_ixpe.BarSelection(bar_area=self.bar_area)
        self.first_done_flag = False
        self.cache = args['cache']

        # ... do something here ...

        os.chdir(ori_dir)  
    
    def __call__(self, input_ctx):
        frame = input_ctx['image']
        output_ctx = {}
        if not self.mat_detector.detect(frame=frame):
            print('no material detected, continue')
            return output_ctx
        bar_roi, abs_point = self.bar_selector.select(frame=frame)
        if abs_point != (0, 0):
            if not self.first_done_flag:
                self.first_done_flag = True
                print('select bar roi success')
            output_ctx["bar_roi"] = bar_roi
            output_ctx["abs_point"] = abs_point
            output_ctx["frame"] = frame
        return output_ctx
        
if __name__ == '__main__':
    args = {
            "d_area" : [(440, 370), (790, 500)],
            "bar_area" : [(80, 390), (1130, 440), (80, 440), (1130, 490)]
    }

    preprocessor = VideoPreprocess(args)
    filename = "/Volumes/Untitled/video/ixpe.mp4"
    import cv2
    video_cap = cv2.VideoCapture(filename)

    ret, frame = video_cap.read()

    while ret:
        ret, frame = video_cap.read()

        input_ctx = dict()
        input_ctx['image'] = frame
        output_ctx = preprocessor(input_ctx)
        print('stage 1')

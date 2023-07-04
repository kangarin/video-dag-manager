import video_preprocess
import generate_super_resolution
import calculate_position
import edge_observe
import cache_service
import time
import cv2

if __name__ == '__main__':

    cache = cache_service.CacheAPI_impl()
    args = {
            "d_area" : [(440, 370), (790, 500)],
            "bar_area" : [(80, 390), (1130, 440), (80, 440), (1130, 490)],
            "cache" : cache
    }

    preprocessor = video_preprocess.VideoPreprocess(args)
    sr_generator = generate_super_resolution.GenerateSuperResolution(args)
    pos_calculator = calculate_position.CalculatePosition(args)
    edge_observer = edge_observe.EdgeObserve(args)
    filename = "/Volumes/Untitled/video/ixpe.mp4"
    import cv2
    video_cap = cv2.VideoCapture(filename)

    ret, frame = video_cap.read()

    while ret:
        ret, frame = video_cap.read()

        input_ctx = dict()
        input_ctx['image'] = frame
        
        start1 = time.time()
        output_ctx1 = preprocessor(input_ctx)
        end1 = time.time()
        print('time of stage 1: {}'.format(end1 - start1))
        # print('stage 1')
        start2 = time.time()
        output_ctx2 = sr_generator(output_ctx1)
        end2 = time.time()
        print('time of stage 2: {}'.format(end2 - start2))
        # print('stage 2')
        start3 = time.time()
        output_ctx3 = pos_calculator(output_ctx2)
        end3 = time.time()
        print('time of stage 3: {}'.format(end3 - start3))
        # print('stage 3')
        start4 = time.time()
        output_ctx4 = edge_observer(output_ctx3)
        end4 = time.time()
        print('time of stage 4: {}'.format(end4 - start4))
        # print('stage 4')
        # show result image
        if 'frame' in output_ctx4:
            lps = output_ctx4['lps']
            rps = output_ctx4['rps']
            # write the lps and rps on the image
            cv2.putText(output_ctx4['frame'], 'lps: {}'.format(lps), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(output_ctx4['frame'], 'rps: {}'.format(rps), (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow('frame', output_ctx4['frame'])
            cv2.waitKey(1)

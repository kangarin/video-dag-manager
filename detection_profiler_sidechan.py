import time
import cv2
import base64
import requests

                    # case 1
                    # "type": "res_profile_frame",
                    # "job_uid": job_uid,
                    # "image_type": "jpeg",
                    # "image_bytes": frame,
                    # "cam_frame_id": cam_frame_id,

                    # case 2
                    # "type": "fps_profile_frames",
                    # "index": cam_frame_id % det_profiler_interval,
                    # "job_uid": job_uid,
                    # "image_type": "jpeg",
                    # "image": frame,
                    # "cam_frame_id": cam_frame_id,


def send_to_detection_profiler_service_res_frame(context):

    frame = context["image"]
    # 将帧编码为Base64字符串
    _, img_encoded = cv2.imencode('.jpg', frame)
    frame_base64 = base64.b64encode(img_encoded).decode('utf-8')

    # 构建包含帧和其他字段信息的请求数据
    payload = {
        'image': frame_base64,
        'job_uid': context["job_uid"],
        'cam_frame_id': context["cam_frame_id"],
        'type': context["type"],
        'image_type': context["image_type"],
        'det_scene': context["det_scene"],
        'cur_video_conf': context["cur_video_conf"],
        'user_constraint': context["user_constraint"],
    }

    if context["type"] == "fps_profile_frames":
        payload["index"] = context["index"]

    # 发送POST请求
    response = requests.post('http://localhost:6984/receive_frame', json=payload)


def send_to_detection_profiler_service_fps_frames(context_list):

    image_list = []
    for i in range(len(context_list)):
        frame = context_list[i]["image"]
        # 将帧编码为Base64字符串
        _, img_encoded = cv2.imencode('.jpg', frame)
        frame_base64 = base64.b64encode(img_encoded).decode('utf-8')
        image_list.append(frame_base64)

    # 构建包含帧和其他字段信息的请求数据
    payload = {
        'image_list': image_list,
        'job_uid': context_list[0]["job_uid"],
        'cam_frame_id': context_list[0]["cam_frame_id"],
        'type': context_list[0]["type"],
        'image_type': context_list[0]["image_type"],
        'det_scene': context_list[0]["det_scene"],
        'cur_video_conf': context_list[0]["cur_video_conf"],
        'user_constraint': context_list[0]["user_constraint"],
    }

    # 发送POST请求
    response = requests.post('http://localhost:6984/receive_frame', json=payload)




def detection_profiler_sidechan_loop(q, det_profiler_continuous_frames):
    local_fps_frames_buffer = []
    while True:
        res = q.get()
        if res['type'] == 'res_profile_frame':
            print("send res frame to detection profiler service!!!!!!")
            send_to_detection_profiler_service_res_frame(res)
        elif res['type'] == 'fps_profile_frames':
            local_fps_frames_buffer.append(res)
            if(len(local_fps_frames_buffer) == det_profiler_continuous_frames):
                print("send fps frames to detection profiler service!!!!!!")
                send_to_detection_profiler_service_fps_frames(local_fps_frames_buffer)
                local_fps_frames_buffer = []
        pass


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        context1 = {"type": "res_profile_frame",
                    "job_uid": "job_uid",
                    "image_type": "jpeg",
                    "image": frame,
                    "cam_frame_id": 1,
                    "det_scene": "face_detection",
                    "cur_video_conf": {},
                    "user_constraint": {}
        }
        
        context2 = {"type": "fps_profile_frames",
                    "index": 1,
                    "job_uid": "job_uid",
                    "image_type": "jpeg",
                    "image": frame,
                    "cam_frame_id": 1,
                    "det_scene": "car_detection",
                    "cur_video_conf": {},
                    "user_constraint": {}
        }
        send_to_detection_profiler_service(context2)
        time.sleep(1)
        pass
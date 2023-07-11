## Job类

- job的状态
  - 未调度 0
  - 就绪态 1
  - 运行态 2
- job拥有的属性
  - 全局唯一id
  - 属于的jobManager
  - 所属结点信息
  - 所用视频信息
  - pipeline
  - 当前状态
  - 工作线程
  - sniffer
  - current_runtime
  - 调度相关（用户约束、flow_mapping、视频配置）
  - keepalive的http客户端，用于请求计算服务

## JobManager类

- 拥有的成员
  - cloud_addr
  - local_addr
  - 计算服务url字典
  - keepalive的http客户端
  - 本地视频流
  - 发到本地的job字典
- 函数
  - 接入query manager（join）
  - 获取计算服务url
  - 更新调度计划
  - ==获取运行时情境==
  - 启动新的job
  - 同步job的结果

## query_manager.py

- user_submit_query_cbk

  - 接受 POST 请求中 JSON 数据，获取 `node_addr`（边缘节点地址）、`video_id`（视频流 ID）、`pipeline`（处理数据的 pipeline）、`user_constraint`（用户约束条件）等信息。

    生成一个唯一的 `job_uid`（任务 ID），创建一个字典 `new_job_info`，存放任务的相关信息。

  - 调用 `query_manager.submit_query()` 方法，将任务信息写到数据库中，等待边缘节点处理。

  - 向指定的边 缘节点发送 POST 请求 `/job/submit_job`，请求体为新创建的任务信息 `new_job_info`。

  - 向边缘节点请求成功后，返回一个 JSON 响应，其中包含 `status`、`msg`、`query_id`、`r_sidechan` 等字段，分别代表 API 的返回码、返回信息、任务 ID 和更新的边缘节点信息。这些信息可以用于日志记录和下一步处理。

  - 值得一提的是，这个 API 的功能不仅仅是将任务提交给边缘节点，还向云端的管理节点（`manager`）注册任务实例和维护任务执行结果等信息，同时还负责更新边缘节点的 sidechannel 信息，确保任务能够正确地分配到边缘节点上执行。



# serveice_demo

==请求5500的计算服务==

- 主函数，启动了一个后台线程，通过调用 start_serv_listener 函数启动一个服务监听器，用于实现外部输入数据的接受以及计算结果的输出。该函数会在指定端口上监听输入的数据，并将其推入到任务队列中等待计算服务进程进行处理。接着，主函数进入一个循环，通过调用 time.sleep 函数来持续休眠 4 秒钟，并在每次休眠结束后记录一个警告，**以便用于进一步调试和监控**。
- get_serv_cbk(**/execute_task/<serv_name>**)先检查服务是否已注册，然后进程池处理请求并返回
  - cal 进程池处理请求



# query_manager

- 启动了一个QueryFlask的线程，使用start_query_listener函数在指定端口上启动一个Flask服务，用于实现输入查询的接收和处理
- 然后，代码通过调用 query_manager.set_service_cloud_addr 函数将计算服务所在的云端地址设置为刚才提取出的地址，以便之后查询管理器与计算服务之间的交互。
- 接下来，代码使用 multiprocessing 模块创建一个新的进程，调用 cloud_sidechan.init_and_start_video_proc 函数来初始化并启动视频流处理，这个过程涉及到从云端向边端转发请求。
- 最后，代码通过调用 cloud_scheduler_loop 函数来启动一个循环，用于定期获取新的查询任务并将其分配给云端或边端的计算服务进行处理。
  - 获取资源情境`http://127.0.0.1:5500/get_resource_info` **(定死？)**
  - 访问已注册的所有job实例，获取实例中保存的结果，生成调度策略
  - 获取当前query的运行时情境并更新`"http://{}/job/get_runtime/{}".format(node_addr, query_id)`
  - 调用调度器
  - 更新调度策略
  - 将调度策略更新到对应结点`"http://{}/job/update_plan".format(node_addr)`

# job_manager

- main: 
  - 分别得到查询管理器的地址、追踪管理器的端口和计算服务的云端地址。
  - 之后，代码启动了一个名为 TrackerFlask 的线程，并使用 start_tracker_listener 函数在指定端口上启动了一个 Flask 服务，用于监控等待追踪管理器的指令。
  - 接着，代码调用了 job_manager.join_query_controller 函数，将自身请求加入到查询控制器中，用于接收和处理外部发起的视频流查询请求。
  - 然后，代码通过 job_manager.set_service_cloud_addr 函数设置了计算服务所在的云端地址。
  - 接下来，代码使用 multiprocessing 模块创建一个新的进程，调用 edge_sidechan.init_and_start_video_proc 函数来初始化并启动视频流处理的接收器，这个过程涉及到从边缘端向云端转发请求。
  - 最后，代码进入一个循环，通过不断调用 job_manager.start_new_job 函数来启动一个新作业，用于处理查询任务并生成相应的视频流处理结果。

- worker_loop:

  - 初始化数据流来源

  - 逐帧汇报结果，逐帧汇报运行时情境

    - **按照指定的 pipeline 对视频流进行处理，并逐帧生成处理结果**。代码首先调用 self.get_job_uid 函数得到当前作业的唯一标识符 job_uid，然后调用 sfg_get_next_init_task 函数来获取一个初始化处理任务的相关参数 cam_frame_id、conf_frame_id 和 output_ctx。

      接下来，代码遍历全部 pipeline 中的任务，依次执行处理并得到任务的输出结果 output_ctx。这里通过调用 `self.manager.get_chosen_service_url` 函数来根据当前待执行任务的名称 taskname 和任务的序号 choice，在服务列表中获取与之对应的服务地址 url。之后，代码调用 `self.invoke_service `函数实现了对服务的远程调用。具体来说，它通过 HTTP POST 请求将任务相关参数传递到远端，等待远端将任务结果通过 HTTP 响应进行返回。如果调用服务失败，代码通过一定时间的等待和重新尝试，直到服务正常返回结果为止。

      接下来，代码使用 `update_runtime` 函数来记录每个服务任务在运行时所消耗的时间，得到的结果会被存储在作业信息中，用于后续的瓶颈分析和优化。同时，代码还使用 update_runtime 函数将服务运行结果存储到输出上下文 output_ctx 中。在执行完全部的任务之后，代码将输出帧以及执行计划结果保存到 frame_result 和 plan_result 中，并返回处理结果。

    - 使用一个循环遍历计划执行结果 plan_result 中的每个任务 taskname，通过累加每个任务运行时延的平均值来**计算全部任务的平均时延** total_frame_delay。之后，代码调用 update_runtime 函数将 end_pipe 任务的运行**时延时长存储**到输出上下文中，并将这个上下文对象的属性 cam_frame_id、n_loop 和 total_frame_delay 存储到 output_ctx 中。

      接下来，代码将 output_ctx 更新到输出帧的结果 frame_result 中，并通过 sync_job_result 函数将处理结果**同步**到查询管理器中。在同步处理结果之前，代码调用 self.get_plan 函数将执行计划的相关信息更新到作业的最新计划属性中。具体来说，这个函数会对计划进行序列化和哈希操作，并返回一个散列码，用于后续比较计划是否发生了变化。最后，代码更新 curr_cam_frame_id 和 curr_conf_frame_id 的值，用于标识下一帧图像的帧 ID 和配置 ID。



# 端口对应的服务

- 5500：
  - /get_service_list
  - /get_resource_info
  - /get_cluster_info
  - /execute_task/<serv_name>

- 5000：
  - /query/submit_query  \# 接受用户提交视频流查询 递归请求：/job/submit_job
    - 路由处理函数从 Flask 的 request 对象中解析出了 HTTP 请求中提交的 JSON 参数，其中包括节点地址、视频流 ID、处理 pipeline 以及用户约束条件等。之后，它生成了一个新的作业 ID 作为作业唯一标识符，并将任务信息提交给了 query_manager，由其进一步调度和处理。接着，路由处理函数调用了 HTTP POST 请求，将任务信息发送到对应节点地址的边缘端服务器上，并将边缘端返回的响应信息 r 传递给了查询管理器。最后，路由处理函数调用了 query_manager.sess.post 函数更新 sidechan 信息，并返回了一个 JSON 格式的响应，表示任务成功提交的状态信息和作业的唯一标识符（即查询 ID）。
  - /query/sync_result
  - /query/get_result/<query_id>
  - /query/get_plan/<query_id>
  - /query/get_runtime/<query_id>
  - /query/get_agg_info/<query_id>
  - /node/get_video_info
  - /node/join

- 5001：



# 调度相关

## 冷启动

这段代码看起来是一个资源分配的函数，可以大概分为以下几个步骤：
1. 遍历所有可用的fps、分辨率和流信息。
2. 根据任务知识库和输入参数预测延迟和精度。
3. 如果延迟符合用户要求，则找到最符合精度要求的配置。
4. 如果延迟不符合用户要求，则找到符合要求的延迟最接近的配置。
5. 返回前一个任务的视频配置和流映射。

其中，get_flow_map、get_pred_delay和get_pred_acc可能是预测函数，能够根据输入参数返回某些结果，而cold_video_conf和cold_flow_mapping则是被更新的结果。

## 运行时情境

```bash
runtime_info = {'delay': 0.3066457410653432, 'obj_n': 20.75, 'obj_size': 2335.908716666574, 'obj_stable': False}
{'face_detection': {'model_id': 0, 'node_role': 'host', 'node_ip': '127.0.0.1'}, 'face_alignment': {'model_id': 0, 'node_role': 'cloud', 'node_ip': '127.0.0.1'}}
```



# 小记录&小疑问

- 获取资源情境是王&戴？
  ```python
  r = query_manager.sess.get(
                  url="http://{}/get_resource_info".format(query_manager.service_cloud_addr))
              resource_info = r.json()
  ```

- 运行时情境指
  ```bash
  runtime_info = {'delay': 0.3066457410653432, 'obj_n': 20.75, 'obj_size': 2335.908716666574, 'obj_stable': False}
  {'face_detection': {'model_id': 0, 'node_role': 'host', 'node_ip': '127.0.0.1'}, 'face_alignment': {'model_id': 0, 'node_role': 'cloud', 'node_ip': '127.0.0.1'}}
  ```

- 调度提供的信息：Job_id、dag图、阶段需要的资源、运行时情境、用户约束；
- 目前PID调度的方法：
  - 没有运行时情境/用户约束则采用冷启动，利用kb来选择能够满足约束的配置
  - 根据实际时延和用户约束来调整视频配置和切分点
  - 好像没有考虑机器的状态
- 目前好像没有涉及到边边？




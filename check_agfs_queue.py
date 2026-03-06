import time
from openviking.storage.queuefs import init_queue_manager
from pyagfs import AGFSClient
import asyncio

client = AGFSClient("http://localhost:1833", timeout=30)  # 增加超时时间
queue_manager = init_queue_manager(
                agfs=client,
                timeout=30,
                max_concurrent_embedding=10,
                max_concurrent_semantic=10,
            )

# 监控队列处理进度
while True:
    status = asyncio.run(queue_manager.check_status("Semantic"))
    print(f"Queue Status: {status}")
    try:
        # 检查队列目录是否存在
        queue_files = client.ls("/queue")
        print(f"Queue files: {queue_files}")

        # 检查 Semantic 队列目录
        semantic_files = client.ls("/queue/Semantic")
        print(f"Semantic queue files: {semantic_files}")

        # 尝试读取 size 文件
        size_content = client.read("/queue/Semantic/size")
        print(f"Queue size: {size_content}")

    except Exception as e:
        print(f"AGFS 操作失败: {e}")
    time.sleep(5)


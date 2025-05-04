#!/usr/bin/env python
import pika
import sys

# --- 連接參數 ---
# 使用預設 guest/guest 帳號密碼連接本地 RabbitMQ
# 如果你的 RabbitMQ 在不同主機或使用不同帳密，請修改這裡
credentials = pika.PlainCredentials('guest', 'guest')
parameters = pika.ConnectionParameters('localhost', 5672, '/', credentials)

connection = None # 在 finally 中需要檢查
try:
    # 1. 連接到代理程式
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    print("成功連接到 RabbitMQ")

    # 2. 聲明交換器和佇列
    # 聲明名為 'my_exchange' 的 direct 交換器
    channel.exchange_declare(exchange='my_exchange', exchange_type='direct')
    print("交換器 'my_exchange' 已聲明")

    # 聲明名為 'my_queue' 的持久化佇列
    # durable=True 確保 RabbitMQ 重啟後佇列依然存在
    channel.queue_declare(queue='my_queue', durable=True)
    print("佇列 'my_queue' 已聲明")

    # 3. 將佇列繫結到交換器
    # 使用繫結鍵 'my_key'
    channel.queue_bind(queue='my_queue', exchange='my_exchange', routing_key='my_key')
    print("佇列 'my_queue' 已繫結到交換器 'my_exchange' (繫結鍵: 'my_key')")

    # 4. 發布訊息
    message_body = "Hello World from Pika!"
    # 發布訊息到 'my_exchange'，使用路由鍵 'my_key'
    # 注意：pika 的 basic_publish 不需要單獨創建 Message 物件
    # properties=pika.BasicProperties(delivery_mode=2) 使訊息持久化 (如果佇列也持久化)
    channel.basic_publish(
        exchange='my_exchange',
        routing_key='my_key',
        body=message_body,
        properties=pika.BasicProperties(
            delivery_mode = 2, # make message persistent
        )
    )
    print(f"訊息 '{message_body}' 已發布")

    print(" [*] 等待訊息。按 CTRL+C 退出")

    # 5. 消費訊息 (使用 basic_get 獲取單條訊息)
    # basic_get 會立即嘗試獲取一條訊息，如果佇列為空則返回 None
    # no_ack=False (預設) 表示需要手動確認
    method_frame, header_frame, body = channel.basic_get(queue='my_queue', auto_ack=False)

    if method_frame:
        print(f"訊息已接收: {body.decode()}")
        # 6. 確認訊息處理完畢
        # delivery_tag 是 RabbitMQ 用來標識特定訊息投遞的標籤
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        print("訊息已確認 (ack)")
    else:
        print("佇列 'my_queue' 中沒有訊息。")

except pika.exceptions.AMQPConnectionError as e:
    print(f"無法連接到 RabbitMQ: {e}", file=sys.stderr)
except Exception as e:
    print(f"發生錯誤: {e}", file=sys.stderr)
finally:
    # 7. 清理：關閉連接
    if connection is not None and connection.is_open:
        connection.close()
        print("連接已關閉")
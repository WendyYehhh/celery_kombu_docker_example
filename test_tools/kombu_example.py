#!/usr/bin/env python
import time
from kombu import Connection, Exchange, Queue, Producer, Consumer

# --- 1. 設定 Broker、交換器和佇列 ---

# RabbitMQ 連接 URL (使用預設 guest:guest 帳號密碼連接本地 RabbitMQ)
BROKER_URL = 'amqp://guest:guest@localhost:5672//'

# 定義一個 Direct 類型的交換器
# direct 交換器會根據 routing_key 精確匹配來路由訊息
direct_exchange = Exchange('kombu.direct.example', 'direct')

# 定義一個佇列，將其綁定到上面的交換器，並指定 routing_key
# 只有 routing_key 完全匹配 'my_routing_key' 的訊息才會被路由到這個佇列
task_queue = Queue(
    name='kombu.direct.queue',    # 佇列名稱
    exchange=direct_exchange,    # 綁定的交換器
    routing_key='my_routing_key' # 繫結鍵/路由鍵
)

# --- 2. 發布訊息 ---

def publish_message():
    """連接到 RabbitMQ 並發布一條訊息"""
    print("[Publisher] 開始發布訊息...")
    # 要發送的訊息內容 (Python 字典)
    message_payload = {
        'message': 'Hello from Kombu Direct Example!',
        'timestamp': time.time(),
        'source': 'kombu_publisher'
    }

    try:
        # 建立到 Broker 的連接
        # 使用 'with' 語句確保連接在使用後能自動關閉
        with Connection(BROKER_URL) as connection:
            print(f"[Publisher] 已連接到: {connection.as_uri()}")

            # 創建一個 Producer 實例
            # serializer='json' 指定訊息體使用 JSON 格式序列化
            producer = Producer(connection, serializer='json')

            print(f"[Publisher] 準備發布訊息: {message_payload}")
            # 發布訊息
            producer.publish(
                message_payload,                # 訊息主體 (會被序列化)
                exchange=direct_exchange,       # 指定要發送到的交換器
                routing_key='my_routing_key',   # 指定路由鍵
                declare=[task_queue],           # 自動聲明佇列和交換器 (如果不存在)
                                                # 這會確保佇列、交換器及它們之間的繫結存在
                retry=True,                     # 啟用內建的發布重試機制 (可選)
                retry_policy={                  # 重試策略 (可選)
                    'interval_start': 0,        # 第一次重試前等待 0 秒
                    'interval_step': 2,         # 後續重試間隔增加 2 秒
                    'interval_max': 30,         # 最大重試間隔 30 秒
                    'max_retries': 3            # 最多重試 3 次
                }
            )
            print("[Publisher] 訊息已成功發布！")

    except ConnectionRefusedError:
        print(f"[Publisher] 錯誤：無法連接到 RabbitMQ ({BROKER_URL})。請確認 RabbitMQ 正在運行。")
    except Exception as e:
        print(f"[Publisher] 發布訊息時發生錯誤: {e}")
    finally:
        print("[Publisher] 發布流程結束。")
    print("-" * 20)


# --- 3. 消費訊息 ---

# 使用一個全域變數來簡單地標示是否已收到訊息，以便結束消費
message_received = False

def handle_message(body, message):
    """處理接收到訊息的回調函數"""
    global message_received
    print("\n[Consumer] 訊息已接收！")
    print(f"  訊息體 (已反序列化): {body!r}") # body 是經 Kombu 自動反序列化的 Python 物件
    # print(f"  原始訊息屬性: {message.properties}")
    # print(f"  投遞資訊: {message.delivery_info}")

    # **重要**: 確認訊息已被成功處理
    # 這會告訴 RabbitMQ 可以從佇列中安全地移除該訊息
    message.ack()
    print("[Consumer] 訊息已確認 (acknowledged)。")
    message_received = True # 設定標誌，以便主循環可以退出


def consume_messages():
    """連接到 RabbitMQ 並開始消費訊息"""
    print("[Consumer] 開始消費訊息...")

    try:
        # 建立連接
        with Connection(BROKER_URL) as connection:
            print(f"[Consumer] 已連接到: {connection.as_uri()}")

            # 創建 Consumer 實例
            # queues=[task_queue]: 指定要消費的佇列列表
            # callbacks=[handle_message]: 指定處理訊息的回調函數列表
            # accept=['json']: 指定可以接受的內容類型 (配合 Producer 的 serializer)
            consumer = Consumer(connection, queues=[task_queue], callbacks=[handle_message], accept=['json'])

            print("[Consumer] 消費者已啟動，等待訊息中... (最多等待 10 秒)")
            consumer.consume() # 開始監聽指定佇列

            # 讓消費者運行一段時間來接收訊息
            # drain_events 會處理收到的訊息並調用回調函數
            # 在這個範例中，我們等待直到 handle_message 被調用或超時
            start_time = time.time()
            timeout_seconds = 10
            while not message_received and (time.time() - start_time) < timeout_seconds:
                try:
                    # 處理 broker 的事件，timeout=1 表示最多阻塞 1 秒等待事件
                    connection.drain_events(timeout=1)
                except TimeoutError: # Python 3 specific, use socket.timeout in Python 2
                    # 如果 drain_events 超時，繼續循環檢查 message_received 狀態
                    pass
                except KeyboardInterrupt:
                    print("\n[Consumer] 收到 Ctrl+C，正在退出...")
                    break # 允許透過 Ctrl+C 提前退出

            if message_received:
                print("[Consumer] 已處理訊息，消費結束。")
            else:
                 print(f"[Consumer] 在 {timeout_seconds} 秒內未收到訊息，消費結束。")

            # Kombu 的 Consumer 在退出 'with' 區塊時會自動取消 (cancel)
            # consumer.cancel() # 可以手動取消

    except ConnectionRefusedError:
        print(f"[Consumer] 錯誤：無法連接到 RabbitMQ ({BROKER_URL})。請確認 RabbitMQ 正在運行。")
    except Exception as e:
        print(f"[Consumer] 消費訊息時發生錯誤: {e}")
    finally:
        print("[Consumer] 消費流程結束。")
    print("-" * 20)


# --- 主執行流程 ---
if __name__ == '__main__':
    # 1. 先發布訊息
    publish_message()

    # 等待一小段時間，確保訊息到達佇列
    print("\n等待 2 秒...\n")
    time.sleep(2)

    # 2. 再消費訊息
    consume_messages()
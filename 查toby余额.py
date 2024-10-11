from web3 import Web3
import threading
from queue import Queue

# 连接到 Base 链
w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))

# 合约地址（转换为校验和地址）
contract_address = Web3.toChecksumAddress('0xb8d98a102b0079b69ffbc760c8d857a31653e56e')#toby合约

# balanceOf 函数签名
balance_of_signature = w3.keccak(text="balanceOf(address)").hex()[:10]

# 假设代币有 18 位小数，如果不是，请修改这个值
DECIMALS = 18

# 创建一个队列来存储地址和序号
address_queue = Queue()

# 创建一个列表来存储结果
results = []

# 查询余额的函数
def query_balance():
    while True:
        item = address_queue.get()
        if item is None:
            break
        index, address = item
        try:
            data = balance_of_signature + '0' * 24 + address[2:]
            balance = w3.eth.call({'to': contract_address, 'data': data})
            balance = int(balance.hex(), 16)
            real_balance = balance // 10**DECIMALS
            result = f"{index}地址 {address} 的代币余额: {real_balance}"
            print(result)  # 打印结果
            results.append(result)
        except Exception as e:
            error_msg = f"{index}地址 {address} 查询时出错: {str(e)}"
            print(error_msg)  # 打印错误信息
            results.append(error_msg)
        finally:
            address_queue.task_done()

# 读取地址列表并放入队列，，一行一地址
with open('地址.txt', 'r') as f:
    for index, line in enumerate(f, 1):
        address_queue.put((index, Web3.toChecksumAddress(line.strip())))

# 创建并启动3个线程
threads = []
for _ in range(3):
    t = threading.Thread(target=query_balance)
    t.start()
    threads.append(t)

# 等待所有地址处理完毕
address_queue.join()

# 停止线程
for _ in range(3):
    address_queue.put(None)
for t in threads:
    t.join()

# 将结果写入文件
with open('toby.txt', 'w') as f:
    for result in results:
        f.write(result + '\n')

print("查询完成，结果已保存到 toby.txt")
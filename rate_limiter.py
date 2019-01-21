# -*- coding: utf-8 -*-

# @Date  :  19-1-21 上午11:47
# @Author:  pubcoder_wj

import asyncio
import uvloop
import time

_128k = 128 * 1024
_256k = 256 * 1024
_512k = 512 * 1024
_1024k = 1024 * 1024


class TokenBucket(object):
    __slots__ = ['capacity', '_tokens', 'fill_rate', 'timestamp']

    def __init__(self, tokens, fill_rate):
        self.capacity = float(tokens)
        self._tokens = float(tokens)
        self.fill_rate = float(fill_rate)
        self.timestamp = time.time()

    async def consume(self, consume_type='num', tokens=100, block=True, begin_time: int = None, end_time: int = None,
                      timer: str = None, work_handler=None):
        while 1:
            now_time = int(time.time())
            if (begin_time is not None) and (end_time is not None):
                if (now_time < int(begin_time)) or (now_time >= int(end_time)):
                    print(' not in the excuting duration!')
                    break
            if consume_type == 'num':
                # consume the token nums
                pass
            elif consume_type == 'traffic':
                # consume the web traffic
                tokens = len(str(tokens))
            else:
                print('error type')

            if block and tokens > self.tokens:
                deficit = tokens - self._tokens
                delay = deficit / self.fill_rate
                # print('Have {} tokens, need {}; sleeping {} seconds'.format(self._tokens, tokens, delay))
                await asyncio.sleep(delay)

            if tokens <= self.tokens:
                self._tokens -= tokens
                if work_handler:
                    work_handler()
                await self.work_handler()
                print(str(tokens) + " I'm working")

    @property
    def tokens(self):
        if self._tokens < self.capacity:
            now = time.time()
            delta = self.fill_rate * (now - self.timestamp)
            self._tokens = min(self.capacity, self._tokens + delta)
            self.timestamp = now
        return self._tokens

    async def work_handler(self):
        print('do ')


class TokenBucketPool(object):
    def __init__(self, size):
        self._size = size
        self._pools = dict()

    def add_token_bucket(self, bucket_id, total_tokens, pro_rate, consume_rate, consume_type, begin_time, end_time,
                         timer):
        if len(self._pools) < self._size:
            self._pools[bucket_id] = {
                'begin_time': begin_time,
                'end_time': end_time,
                'timer': timer,
                'tb_object': TokenBucket(total_tokens, pro_rate),
                'consume_type': consume_type,
                'consume_rate': consume_rate,
                'is_started': False
            }
        else:
            print('out of the size of token bucket！')

    async def rate_limit(self, bucket_id, token_bucket, consume_type, consume_rate, begin_time, end_time, timer):
        task = asyncio.ensure_future(
            token_bucket.consume(consume_type=consume_type, tokens=consume_rate, begin_time=begin_time,
                                 end_time=end_time, timer=timer))
        self._pools[bucket_id]['task'] = task
        self._pools[bucket_id]['is_started'] = True
        print(self._pools)
        await task

    async def start(self):
        while 1:
            work_list = list()
            for bucket_id, bucket_info in list(self._pools.items()):
                if not (bucket_info['is_started']):
                    work_list.append(asyncio.ensure_future(
                        self.rate_limit(bucket_id, bucket_info['tb_object'], bucket_info['consume_type'],
                                        bucket_info['consume_rate'], bucket_info['begin_time'],
                                        bucket_info['end_time'], bucket_info['timer'])))
            await asyncio.gather(*work_list)
            await asyncio.sleep(1)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    _loop = asyncio.get_event_loop()
    tbp = TokenBucketPool(100)
    # 添加一个限流配置   20次/60s
    bucket_id = 'pp_01'
    total_tokens = 60
    pro_rate = 20
    consume_rate = 60
    consume_type = 'num'
    begin_time = '1547520567'
    end_time = '1557520567'
    timer = None
    tbp.add_token_bucket(bucket_id, total_tokens, pro_rate, consume_rate, consume_type, begin_time, end_time, timer)
    print(tbp._pools)

    # 添加一个限流配置  10次/100s
    bucket_id = 'pp_02'
    total_tokens = 100
    pro_rate = 10
    consume_rate = 100
    consume_type = 'num'
    begin_time = '1547520567'
    end_time = '1557520567'
    timer = None
    tbp.add_token_bucket(bucket_id, total_tokens, pro_rate, consume_rate, consume_type, begin_time, end_time, timer)
    print(tbp._pools)

    # 添加一个限流配置  10/（1-0.2） 之后维持在0.2次/1s
    bucket_id = 'pp_03'
    total_tokens = 10
    pro_rate = 0.2
    consume_rate = 1
    consume_type = 'num'
    begin_time = '1547520567'
    end_time = '1557520567'
    timer = None
    tbp.add_token_bucket(bucket_id, total_tokens, pro_rate, consume_rate, consume_type, begin_time, end_time, timer)
    print(tbp._pools)

    _loop.run_until_complete(tbp.start())

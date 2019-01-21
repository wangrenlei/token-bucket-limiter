# token-bucket-limiter
a center limiter based on the token bucket

# Example
```python
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
```

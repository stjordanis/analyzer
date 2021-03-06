import json
import logging

log=logging.getLogger(__name__)


class TradingEngine(object):
    '''
        has the responsability to execut strategies
        Sends actions to trading center
        does not store anything, used for realtime
    '''
    def __init__(self, redis, strategy, start=None, end=None):
        self.redis = redis
        self.pubsub = redis.pubsub()
        self.strategy = strategy
        self.start = start
        self.end = end
        self.securities = []

    def listen(self, security):
        self.securities.append(security)
        self.pubsub.subscribe(security.symbol)

    def execute(self, security, tick):
        action = self.strategy.update(security, tick)
        if action:
            self.redis.publish('action', {'action': action, 'tick': tick})

    def consume(self):
        for security in self.securities:
            for tick in self.pubsub.listen():
                log.info('New tick {0}'.format(tick))
                if tick['type'] in 'subscribe':
                    continue
                # strategy will create actions
                # traging center will see the actions
                # and will place orders
                tick['data'] = json.loads(tick['data'].decode('utf-8').replace("'", '"').replace('u"', '"'))
                self.execute(security, tick)

from collections import OrderedDict, deque
import random

LARGE_POOL_THRESHOLD = 10_000
RECENCY_BUFFER_SIZE = 1024
MAX_REPLAY_CACHE = 32

_STREAM_BAGS = {}
_REPLAY_CACHE = OrderedDict()


def common_dist(insanitylevel, rng=None, saturate_at_max=True):
    _rng = rng if rng is not None else random
    return _rng.randint(1, 5) < insanitylevel or (saturate_at_max and insanitylevel >= 10)


def normal_dist(insanitylevel, rng=None, saturate_at_max=True):
    _rng = rng if rng is not None else random
    return _rng.randint(1, 10) < insanitylevel or (saturate_at_max and insanitylevel >= 10)


def uncommon_dist(insanitylevel, rng=None, saturate_at_max=True):
    _rng = rng if rng is not None else random
    return _rng.randint(1, 18) < insanitylevel or (saturate_at_max and insanitylevel >= 10)


def rare_dist(insanitylevel, rng=None, saturate_at_max=True):
    _rng = rng if rng is not None else random
    roll = _rng.randint(1, 30) < insanitylevel or (saturate_at_max and insanitylevel >= 10)
    if roll:
        print("adding something rare to the prompt")
    return roll


def legendary_dist(insanitylevel, rng=None, saturate_at_max=True):
    _rng = rng if rng is not None else random
    roll = _rng.randint(1, 50) < insanitylevel
    if roll:
        print("Nice! adding something legendary to the prompt")
    return roll


def unique_dist(insanitylevel, rng=None, saturate_at_max=True):
    _rng = rng if rng is not None else random
    roll = _rng.randint(1, 75) < insanitylevel
    if roll:
        print("Critical hit! Something unique has been added to the prompt")
    return roll


def extraordinary_dist(insanitylevel, rng=None, saturate_at_max=True):
    _rng = rng if rng is not None else random
    roll = _rng.randint(1, 200) < insanitylevel
    if roll:
        print("Extraordinary! Something special has been added to the prompt")
    return roll


def novel_dist(insanitylevel, rng=None, saturate_at_max=True):
    _rng = rng if rng is not None else random
    roll = _rng.randint(1, 500) < insanitylevel
    if roll:
        print("Uh, something novel has been added to the prompt. Interesting.")
    return roll


def chance_roll(insanitylevel, chance, rng=None, saturate_at_max=True):
    _rng = rng if rng is not None else random
    chance_mapping = {
        'never': {'set_number': 0, 'message': ""},
        'novel': {'set_number': 500, 'message': "Uh, something novel has been added to the prompt. Interesting."},
        'extraordinary': {'set_number': 200, 'message': "Extraordinary! Something special has been added to the prompt"},
        'unique': {'set_number': 75, 'message': "Critical hit! Something unique has been added to the prompt"},
        'legendary': {'set_number': 50, 'message': "Nice! adding something legendary to the prompt"},
        'rare': {'set_number': 30, 'message': "adding something rare to the prompt"},
        'uncommon': {'set_number': 18, 'message': ""},
        'normal': {'set_number': 10, 'message': ""},
        'common': {'set_number': 5, 'message': ""},
        'always': {'set_number': 1, 'message': ""},
    }
    if chance == 'never':
        return False
    if chance in chance_mapping:
        properties = chance_mapping[chance]
        set_number = properties['set_number']
        message = properties['message']
        # if we have insanity level of 10, then every under rare is always true
        if saturate_at_max and set_number <= 35 and insanitylevel >= 10:
            if message != "":
                print(message)
            return True
        roll = _rng.randint(1, set_number) < insanitylevel
        if message != "" and roll:
            print(message)
        return roll
    raise ValueError(f"Invalid chance value: {chance}")


class _SmallPoolState:
    def __init__(self, size, rng):
        self.size = size
        self.order = list(range(size))
        rng.shuffle(self.order)
        self.pos = 0
        self.last_idx = None

    def next_index(self, rng):
        if self.pos >= self.size:
            self.order = list(range(self.size))
            rng.shuffle(self.order)
            if self.size > 1 and self.order[0] == self.last_idx:
                swap_pos = rng.randint(1, self.size - 1)
                self.order[0], self.order[swap_pos] = self.order[swap_pos], self.order[0]
            self.pos = 0
        idx = self.order[self.pos]
        self.pos += 1
        self.last_idx = idx
        return idx


class _LargePoolState:
    def __init__(self, size):
        self.size = size
        self.recent_queue = deque(maxlen=RECENCY_BUFFER_SIZE)
        self.recent_set = set()

    def next_index(self, rng):
        idx = rng.randrange(self.size)
        for _ in range(16):
            if idx not in self.recent_set:
                break
            idx = rng.randrange(self.size)
        if len(self.recent_queue) == RECENCY_BUFFER_SIZE:
            evicted = self.recent_queue[0]
            self.recent_set.discard(evicted)
        self.recent_queue.append(idx)
        self.recent_set.add(idx)
        return idx


class ShuffleBag:
    """Cycle-shuffles small/medium pools without boundary repeats and uses O(1) recency sampling for >10k pools."""

    def __init__(self):
        self._pools = {}

    def _get_state(self, pool_key, size, rng):
        state = self._pools.get(pool_key)
        if state is None or state.size != size:
            if size <= LARGE_POOL_THRESHOLD:
                state = _SmallPoolState(size, rng)
            else:
                state = _LargePoolState(size)
            self._pools[pool_key] = state
        return state

    def pick(self, items, key=None, rng=None, exclude=None):
        n = len(items)
        if n == 0:
            raise IndexError("Cannot pick from an empty sequence")
        if n == 1:
            return items[0]
        _rng = rng if rng is not None else random
        if key is not None:
            pool_key = key
        else:
            pool_key = ("anon", n, str(items[0])[:64], str(items[n // 2])[:64], str(items[-1])[:64])
        state = self._get_state(pool_key, n, _rng)

        max_tries = min(n, 16) if exclude else 1
        chosen = items[state.next_index(_rng)]
        if exclude:
            for _ in range(max_tries - 1):
                if chosen not in exclude:
                    break
                chosen = items[state.next_index(_rng)]
        return chosen


class PickContext:
    """Threads deterministic RNG, optional ShuffleBag, and saturation behavior through prompt generation."""

    def __init__(self, rng=None, bag=None, use_bag=False, saturate_at_max=True):
        self.rng = rng if rng is not None else random
        self.bag = bag
        self.use_bag = bool(use_bag and bag is not None)
        self.saturate_at_max = saturate_at_max

    def randint(self, a, b):
        return self.rng.randint(a, b)

    def randrange(self, *args):
        return self.rng.randrange(*args)

    def random(self):
        return self.rng.random()

    def choice(self, seq):
        return self.rng.choice(seq)

    def shuffle(self, seq):
        self.rng.shuffle(seq)

    def sample(self, population, k):
        return self.rng.sample(population, k)

    def pick(self, items, key=None, exclude=None):
        if self.use_bag:
            return self.bag.pick(items, key=key, rng=self.rng, exclude=exclude)
        if not items:
            raise IndexError("Cannot pick from an empty sequence")
        if exclude and len(items) > 1:
            for _ in range(min(len(items), 16)):
                candidate = self.rng.choice(items)
                if candidate not in exclude:
                    return candidate
        return self.rng.choice(items)

    def chance(self, insanitylevel, chance_name):
        return chance_roll(insanitylevel, chance_name, rng=self.rng, saturate_at_max=self.saturate_at_max)


def get_stream_bag(stream_key):
    bag = _STREAM_BAGS.get(stream_key)
    if bag is None:
        bag = ShuffleBag()
        _STREAM_BAGS[stream_key] = bag
    return bag


def get_replay_result(cache_key):
    if cache_key in _REPLAY_CACHE:
        _REPLAY_CACHE.move_to_end(cache_key)
        return _REPLAY_CACHE[cache_key]
    return None


def set_replay_result(cache_key, value):
    _REPLAY_CACHE[cache_key] = value
    _REPLAY_CACHE.move_to_end(cache_key)
    while len(_REPLAY_CACHE) > MAX_REPLAY_CACHE:
        _REPLAY_CACHE.popitem(last=False)

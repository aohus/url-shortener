import string
import threading
import time

from adapter.repository import SqlAlchemyRepository
from domain import model
from sqlalchemy.orm import Session


class IdGenerator:
    def __init__(self, node_id: int, epoch: int = 1609459200000):
        self.node_id = node_id
        self.epoch = epoch
        self.node_id_bits = 10
        self.sequence_bits = 12
        self.max_node_id = (1 << self.node_id_bits) - 1
        self.max_sequence = (1 << self.sequence_bits) - 1
        self.node_id_shift = self.sequence_bits
        self.timestamp_shift = self.sequence_bits + self.node_id_bits
        self.last_timestamp = -1
        self.sequence = 0
        self.lock = threading.Lock()

        if self.node_id > self.max_node_id:
            raise ValueError(f"Node ID must be between 0 and {self.max_node_id}")

    def _current_timestamp(self):
        return int(time.time() * 1000)

    def _wait_for_next_millis(self, last_timestamp):
        timestamp = self._current_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._current_timestamp()
        return timestamp

    def generate_id(self):
        with self.lock:
            timestamp = self._current_timestamp()

            if timestamp < self.last_timestamp:
                raise Exception("Clock moved backwards. Refusing to generate id")

            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.max_sequence
                if self.sequence == 0:
                    timestamp = self._wait_for_next_millis(self.last_timestamp)
            else:
                self.sequence = 0

            self.last_timestamp = timestamp
            id = (
                ((timestamp - self.epoch) << self.timestamp_shift)
                | (self.node_id << self.node_id_shift)
                | self.sequence
            )
            return id


# Base62 변환 함수
BASE62_ALPHABET = string.digits + string.ascii_letters


def encode_base62(num: int) -> str:
    if num == 0:
        return BASE62_ALPHABET[0]

    base62 = []
    while num:
        num, rem = divmod(num, 62)
        base62.append(BASE62_ALPHABET[rem])
    return "".join(reversed(base62))


node_id = 1  # Assign a unique node ID to each generator instance
generator = IdGenerator(node_id=node_id)


def generate_short_key(original_url: str, repo: SqlAlchemyRepository, session: Session):
    id = generator.generate_id()
    short_key = encode_base62(id)
    model.url(original_url, short_key)
    session.commit()
    return short_key


def get_short_key(original_url: str, repo: SqlAlchemyRepository, session: Session):
    short_key = repo.get(original_url=original_url)
    if short_key:
        return short_key
    generate_short_key(original_url, repo, session)
    return short_key

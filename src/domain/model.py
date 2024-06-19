from dataclasses import dataclass


class URL:
    def __init__(self, original_url: str, short_key: str):
        self.original_url = original_url
        self.short_key = short_key

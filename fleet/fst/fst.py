from typing import Dict


class FST:
    status_map: Dict[str, str] = {}

    def add(self, from_status: str, to_status: str):
        self.status_map[from_status] = to_status

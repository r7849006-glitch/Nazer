#!/usr/init/env python3
# -*- coding: utf-8 -*-

"""
Wave Nexus Bridge: Connects C Core Mining output to Python P2P & BubbleDB
Developer: Amirabbas
"""

import socket
import threading
import json
import time
import os
from datetime import datetime, timezone

class BubbleDB:
    def __init__(self, db_path="bubble_storage.db"):
        self.db_path = db_path
        self.storage = {}
        self.load_disk()

    def put(self, key, value):
        self.storage[key] = {
            "value": value,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        self.flush_disk()

    def get(self, key):
        return self.storage.get(key, {}).get("value", None)

    def flush_disk(self):
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(self.storage, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[BubbleDB Error] {e}")

    def load_disk(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    self.storage = json.load(f)
            except Exception:
                self.storage = {}

class EdgeBridgeNode:
    def __init__(self, port=6000):
        self.port = port
        self.db = BubbleDB(f"bridge_node_{port}_db.json")
        self.running = True

    def ingest_mined_block(self, block_data):
        """دریافت مستقیم بلاک استخراج‌شده از هسته C"""
        block_id = block_data.get("index")
        self.db.put(f"block_{block_id}", block_data)
        print(f" [🌉 C-Bridge] بلاک شماره {block_id} از هسته C دریافت و در BubbleDB ثبت شد!")

if __name__ == "__main__":
    bridge = EdgeBridgeNode(port=6000)
    print(" [🟢 Bridge Node] پل ارتباطی C و BubbleDB فعال شد.")
    
    # شبیه‌سازی دریافت بلاک از هسته C
    sample_c_block = {
        "index": 2,
        "timestamp": time.time(),
        "difficulty": 1.0,
        "harmony": 0.444,
        "transactions_count": 5
    }
    
    bridge.ingest_mined_block(sample_c_block)
    print(f" [🔍 Storage Check]: {bridge.db.get('block_2')}")

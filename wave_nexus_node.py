#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Wave Nexus Node: P2P Network + BubbleDB Engine (Unified Core)
Developer: Amirabbas
"""

import socket
import threading
import json
import time
import os
from datetime import datetime, timezone

# ==============================================================================
# 1. BubbleDB: Memory-Optimized Key-Value & State Storage
# ==============================================================================
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
        """ذخیره‌سازی سریع و فشرده روی دیسک"""
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(self.storage, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[BubbleDB Error] Disk flush failed: {e}")

    def load_disk(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    self.storage = json.load(f)
            except Exception:
                self.storage = {}

# ==============================================================================
# 2. P2P Gossip Node & Asynchronous Sync Engine
# ==============================================================================
class EdgeP2PNode:
    def __init__(self, host="127.0.0.1", port=5000):
        self.host = host
        self.port = port
        self.db = BubbleDB(f"node_{port}_db.json")
        self.peers = set()
        self.running = True

        # راه‌اندازی سرور سوکت برای دریافت بلاک‌ها و تراکنش‌ها
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

    def start(self):
        threading.Thread(target=self._listen_incoming, daemon=True).start()
        print(f" [🟢 P2P Node] نود لبه‌ای روی پورت {self.port} فعال و آماده دریافت شد.")

    def _listen_incoming(self):
        while self.running:
            try:
                conn, addr = self.server_socket.accept()
                threading.Thread(target=self._handle_peer, args=(conn, addr), daemon=True).start()
            except Exception:
                break

    def _handle_peer(self, conn, addr):
        try:
            data = conn.recv(4096).decode('utf-8')
            if data:
                message = json.loads(data)
                self._process_message(message)
        except Exception as e:
            pass
        finally:
            conn.close()

    def _process_message(self, msg):
        m_type = msg.get("type")
        payload = msg.get("payload")

        if m_type == "BLOCK_SYNC":
            block_id = payload.get("block_id")
            txs = payload.get("transactions")
            
            # ذخیره در پایگاه داده BubbleDB
            self.db.put(f"block_{block_id}", txs)
            print(f" [📥 P2P Broadcast] بلاک جدید {block_id} دریافت و در BubbleDB ثبت شد. تراکنش‌ها: {len(txs)}")

    def broadcast(self, message):
        """ارسال پیام به روش Gossip به تمام همتاها"""
        data = json.dumps(message).encode('utf-8')
        for peer in self.peers:
            p_host, p_port = peer.split(":")
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1.0)
                s.connect((p_host, int(p_port)))
                s.sendall(data)
                s.close()
            except Exception:
                pass

    def add_peer(self, peer_address):
        self.peers.add(peer_address)

# ==============================================================================
# تست عملیاتی و اجرای یکپارچه
# ==============================================================================
if __name__ == "__main__":
    node = EdgeP2PNode(host="127.0.0.1", port=6000)
    node.start()

    sample_block = {
        "block_id": 1042,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "transactions": [
            {"from": "User_A", "to": "User_B", "amount": 15.0, "asset": "RVC"},
            {"from": "Mining_Reward", "to": "User_A", "amount": 2.5, "asset": "RVC"}
        ]
    }

    node.add_peer("127.0.0.1:6000")
    node.broadcast({"type": "BLOCK_SYNC", "payload": sample_block})

    time.sleep(1)
    
    saved_data = node.db.get("block_1042")
    print(f" [🔍 BubbleDB Query Result]: {saved_data}")

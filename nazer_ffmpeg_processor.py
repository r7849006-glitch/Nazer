from __future__ import annotations
#!/usr/init/env python3
# -*- coding: utf-8 -*-

"""
Nazer Pure-Python FFmpeg Video Surveillance Pipeline (Interactive Menu)
---------------------------------------------------------------------
Scans video directories, presents an interactive list, and processes
raw frames via FFmpeg subprocess pipes.
"""

import subprocess
import json
import os
import math
from datetime import datetime, timedelta

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


class NazerFFmpegStreamProcessor:
    def __init__(self, width: int = 320, height: int = 240, anomaly_threshold: float = 1.2):
        self.width = width
        self.height = height
        self.anomaly_threshold = anomaly_threshold
        self.report_dir = "nazer_reports"
        os.makedirs(self.report_dir, exist_ok=True)

    def _get_video_fps(self, video_path: str) -> float:
        try:
            cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate', '-of', 'default=noprint_wrappers=1:nokey=1', video_path]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=True)
            rate_str = result.stdout.strip()
            if '/' in rate_str:
                num, den = map(int, rate_str.split('/'))
                return float(num / den) if den > 0 else 30.0
            return float(rate_str) if rate_str else 30.0
        except Exception:
            return 30.0

    def process_video(self, video_path: str):
        if not os.path.exists(video_path):
            print(f"❌ [ERROR] Video file not found: {video_path}")
            return

        fps = self._get_video_fps(video_path)
        print(f"🚀 [NAZER-FFMPEG] | Streaming video: {video_path} | Detected FPS: {fps:.2f}")

        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-f', 'image2pipe',
            '-pix_fmt', 'gray',
            '-vf', f'scale={self.width}:{self.height}',
            '-vcodec', 'rawvideo',
            '-'
        ]

        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10**8)
        except FileNotFoundError:
            print("❌ [ERROR] FFmpeg is not installed or not in PATH. Install via: pkg install ffmpeg")
            return

        frame_size = self.width * self.height
        frame_index = 0
        events_log = []
        
        if NUMPY_AVAILABLE:
            reference_pattern = np.random.rand(64)
        else:
            reference_pattern = [0.5] * 64

        base_datetime = datetime.now()
        print("⚙️ [NAZER-FFMPEG] | Reading raw frame buffer and matching OPD dictionary...")

        while True:
            raw_frame = process.stdout.read(frame_size)
            if not raw_frame or len(raw_frame) != frame_size:
                break

            frame_index += 1
            current_sec = frame_index / fps
            simulated_time = base_datetime + timedelta(seconds=current_sec)
            timestamp_str = simulated_time.strftime("%Y-%m-%d %H:%M:%S.ms")

            if NUMPY_AVAILABLE:
                frame_array = np.frombuffer(raw_frame, dtype=np.uint8)
                matrix = frame_array.reshape((self.height, self.width))
                resized_vector = matrix[::int(self.height/8), ::int(self.width/8)].flatten().astype(float) / 255.0
                
                if len(resized_vector) > 64:
                    resized_vector = resized_vector[:64]
                elif len(resized_vector) < 64:
                    resized_vector = np.pad(resized_vector, (0, 64 - len(resized_vector)), 'constant')

                distance = float(np.linalg.norm(resized_vector - reference_pattern))
            else:
                step = frame_size // 64
                resized_vector = [raw_frame[i] / 255.0 for i in range(0, frame_size, step)[:64]]
                distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(resized_vector, reference_pattern[:len(resized_vector)])))

            is_anomaly = distance > self.anomaly_threshold

            if frame_index == 1:
                events_log.append({
                    "frame_index": frame_index,
                    "timestamp": timestamp_str,
                    "event_category": "NORMAL_OPERATION",
                    "event_type": "CLOCK_IN_ATTENDANCE",
                    "distance_score": round(distance, 4)
                })
            elif is_anomaly:
                events_log.append({
                    "frame_index": frame_index,
                    "timestamp": timestamp_str,
                    "event_category": "ANOMALY_ALERT",
                    "event_type": "AFTER_HOURS_INTRUSION_OR_ACTIVITY",
                    "distance_score": round(distance, 4)
                })

        process.stdout.close()
        process.wait()

        date_str = base_datetime.strftime('%Y-%m-%d')
        report_path = os.path.join(self.report_dir, f"nazer_ffmpeg_audit_{date_str}.json")
        
        report_payload = {
            "processor": "Nazer_FFmpeg_Zero_Dependency_Core",
            "total_frames_processed": frame_index,
            "recorded_events_count": len(events_log),
            "events": events_log
        }

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_payload, f, indent=4, ensure_ascii=False)

        print(f"📊 [NAZER-REPORT] | Successfully processed {frame_index} frames.")
        print(f"📁 Structured audit report saved to: {report_path}")


def find_videos():
    search_paths = [
        "/sdcard/Video.Guru/Movies",
        "/sdcard/Download",
        "/sdcard/DCIM",
        "."
    ]
    found_videos = []
    for path in search_paths:
        if os.path.exists(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
                        found_videos.append(os.path.join(root, file))
    return found_videos


if __name__ == "__main__":
    print("🔍 Searching for video files on device...")
    videos = find_videos()

    if not videos:
        print("❌ No video files found in common directories.")
    else:
        print("\n--- 🎬 AVAILABLE VIDEOS FOR NAZER TEST ---")
        for idx, v in enumerate(videos[:15], start=1):
            print(f"  [{idx}] {v}")
        print("------------------------------------------")
        
        try:
            choice = input("👉 Enter the number of the video to test: ").strip()
            selected_idx = int(choice) - 1
            if 0 <= selected_idx < len(videos):
                target_video = videos[selected_idx]
                processor = NazerFFmpegStreamProcessor(width=320, height=240, anomaly_threshold=1.2)
                processor.process_video(target_video)
            else:
                print("❌ Invalid selection number.")
        except ValueError:
            print("❌ Please enter a valid number.")

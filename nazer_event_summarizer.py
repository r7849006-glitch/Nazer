from __future__ import annotations
#!/usr/init/env python3
# -*- coding: utf-8 -*-

"""
Nazer Event Summarizer & Time-Span Aggregator
---------------------------------------------
Aggregates continuous frame-level anomaly detections into 
structured start/end time-span event intervals.
"""

import json
import os

def summarize_audit_report(json_path: str):
    if not os.path.exists(json_path):
        print(f"❌ Report not found: {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    events = data.get("events", [])
    if not events:
        print("ℹ️ No events found in report.")
        return

    summarized_intervals = []
    current_event = None

    for ev in events:
        t_str = ev.get("timestamp", "00:00:00")
        category = ev.get("event_category", "UNKNOWN")
        score = ev.get("distance_score", 0.0)

        # اگر رویداد جدیدی شروع شده یا نوع آن تغییر کرده است
        if current_event is None:
            current_event = {
                "event_type": category,
                "start_timestamp": t_str,
                "end_timestamp": t_str,
                "frame_count": 1,
                "max_distance_score": score
            }
        else:
            if current_event["event_type"] == category:
                # استمرار رویداد قبلی
                current_event["end_timestamp"] = t_str
                current_event["frame_count"] += 1
                if score > current_event["max_distance_score"]:
                    current_event["max_distance_score"] = score
            else:
                # ثبت رویداد قبلی و شروع بازه جدید
                summarized_intervals.append(current_event)
                current_event = {
                    "event_type": category,
                    "start_timestamp": t_str,
                    "end_timestamp": t_str,
                    "frame_count": 1,
                    "max_distance_score": score
                }

    if current_event:
        summarized_intervals.append(current_event)

    print(f"\n--- 📋 NAZER TIME-SPAN SUMMARY REPORT ---")
    print(f"Total Raw Frames Processed: {data.get('total_frames_processed', 0)}")
    print(f"Aggregated Distinct Event Intervals: {len(summarized_intervals)}\n")

    for idx, interval in enumerate(summarized_intervals, start=1):
        print(f"[{idx}] Type: {interval['event_type']}")
        print(f"    ⏳ Start Time : {interval['start_timestamp']}")
        print(f"    🏁 End Time   : {interval['end_timestamp']}")
        print(f"    🎞️ Frames     : {interval['frame_count']}")
        print(f"    📊 Peak Score : {interval['max_distance_score']}")
        print("-" * 40)

if __name__ == "__main__":
    report_file = "nazer_reports/nazer_ffmpeg_audit_2026-11-13.json"
    summarize_audit_report(report_file)

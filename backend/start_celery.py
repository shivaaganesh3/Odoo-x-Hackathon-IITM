#!/usr/bin/env python3
"""
Celery startup script for SynergySphere scheduled jobs

This script starts both the Celery worker and beat scheduler.
Make sure Redis is running before starting this script.

Usage:
    python start_celery.py [worker|beat|both]

Commands:
    worker - Start only the Celery worker
    beat   - Start only the Celery beat scheduler  
    both   - Start both worker and beat (default)
"""

import sys
import subprocess
import time
import signal
import os
from threading import Thread


def start_worker():
    """Start Celery worker process"""
    print("🚀 Starting Celery worker...")
    cmd = [
        sys.executable, '-m', 'celery', 
        '-A', 'celery_app:celery', 
        'worker', 
        '--loglevel=info',
        '--concurrency=2',
        '--queues=scheduled,celery'
    ]
    return subprocess.Popen(cmd)


def start_beat():
    """Start Celery beat scheduler process"""
    print("⏰ Starting Celery beat scheduler...")
    cmd = [
        sys.executable, '-m', 'celery',
        '-A', 'celery_app:celery',
        'beat',
        '--loglevel=info'
    ]
    return subprocess.Popen(cmd)


def check_redis():
    """Check if Redis is running"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis is running")
        return True
    except Exception as e:
        print(f"❌ Redis is not running: {e}")
        print("Please start Redis server before running Celery")
        return False


def main():
    """Main startup function"""
    if not check_redis():
        sys.exit(1)
    
    mode = sys.argv[1] if len(sys.argv) > 1 else 'both'
    processes = []
    
    try:
        if mode in ['worker', 'both']:
            worker_process = start_worker()
            processes.append(('worker', worker_process))
            
        if mode in ['beat', 'both']:
            # Give worker a moment to start first
            if mode == 'both':
                time.sleep(2)
            beat_process = start_beat()
            processes.append(('beat', beat_process))
        
        if not processes:
            print("❌ Invalid mode. Use: worker, beat, or both")
            sys.exit(1)
            
        print(f"\n🎉 Celery {mode} started successfully!")
        print("📧 Scheduled jobs are now active:")
        print("   • Daily reminders: Every 24 hours")
        print("   • Monthly reports: Every 30 days")
        print("\n💡 To test jobs manually, use:")
        print("   celery -A celery_app:celery call scheduled_jobs.test_daily_reminders")
        print("   celery -A celery_app:celery call scheduled_jobs.test_monthly_reports")
        print("\nPress Ctrl+C to stop all processes...")
        
        # Wait for processes
        for name, process in processes:
            process.wait()
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Celery processes...")
        for name, process in processes:
            print(f"   Stopping {name}...")
            process.terminate()
            process.wait()
        print("✅ All processes stopped.")


if __name__ == '__main__':
    main() 
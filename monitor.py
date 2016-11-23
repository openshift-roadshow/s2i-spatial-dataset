from __future__ import print_function

import os
import time
import atexit

import threading

try:
    import Queue as queue
except ImportError:
    import queue

import psutil
import mod_wsgi

_running = False
_queue = queue.Queue()
_lock = threading.Lock()

_cpu_percentage = 1800 * [0.0]
_processes = {}

_busy_times = 1801 * [0.0]

def _monitor():
    global _cpu_percentage
    global _processes

    global _busy_times

    while True:
        marker = time.time()

        total = 0.0
        pids = psutil.pids()

        processes = {}

        for pid in pids:
            process = _processes.get(pid)
            if process is None:
                process = psutil.Process(pid)
            processes[pid] = process
            total += process.cpu_percent()

        _processes = processes

        _cpu_percentage.insert(0, total)

        _cpu_percentage = _cpu_percentage[:1800]

        metrics = mod_wsgi.process_metrics()

        _busy_times.insert(0, metrics['request_busy_time'])

        _busy_times = _busy_times[:1801]

        duration = max(0.0, 1.0 - (time.time() - marker))

        try:
            return _queue.get(timeout=duration)

        except queue.Empty:
            pass

_thread = threading.Thread(target=_monitor)
_thread.setDaemon(True)

def _exiting():
    try:
        _queue.put(True)
    except Exception:
        pass
    _thread.join()

def track_changes(path):
    if not path in _files:
        _files.append(path)

def start_monitor():
    global _running
    _lock.acquire()
    if not _running:
        prefix = 'monitor (pid=%d):' % os.getpid()
        print('%s Starting CPU monitor.' % prefix)
        _running = True
        _thread.start()
        atexit.register(_exiting)
    _lock.release()

def cpu_averages():
    values = _cpu_percentage[:60]

    averages = {}

    def average(secs):
        return min(100.0, sum(values[:secs])/secs)

    averages['cpu.average.1s'] = average(1)
    averages['cpu.average.5s'] = average(5)
    averages['cpu.average.15s'] = average(15)
    averages['cpu.average.30s'] = average(30)
    averages['cpu.average.1m'] = average(60)
    averages['cpu.average.5m'] = average(300)
    averages['cpu.average.15m'] = average(900)
    averages['cpu.average.30m'] = average(1800)

    return averages

def capacity_averages():
    values = _busy_times[:1801]

    averages = {}

    def average(secs):
        threads = mod_wsgi.threads_per_process
        return min(100.0, 100*((values[0]-values[secs])/secs)/threads)

    averages['capacity.average.1s'] = average(1)
    averages['capacity.average.5s'] = average(5)
    averages['capacity.average.15s'] = average(15)
    averages['capacity.average.30s'] = average(30)
    averages['capacity.average.1m'] = average(60)
    averages['capacity.average.5m'] = average(300)
    averages['capacity.average.15m'] = average(900)
    averages['capacity.average.30m'] = average(1800)

    return averages

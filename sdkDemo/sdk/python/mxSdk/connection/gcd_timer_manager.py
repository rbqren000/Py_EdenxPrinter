import threading
from typing import Dict, List, Optional, Callable, Any
from .gcd_style_timer import GCDStyleTimer
from ..utils.rbq_log import RBQLog

class GCDTimerManager:
    def __init__(self) -> None:
        self._timers: Dict[str, Dict[str, GCDStyleTimer]] = {}  # {group: {name: timer}}
        self._lock: threading.RLock = threading.RLock()

    def _get_group(self, group: str) -> Dict[str, GCDStyleTimer]:
        if group not in self._timers:
            self._timers[group] = {}
        return self._timers[group]

    def add_timer(self, name: str, start: float, interval: float, callback: Callable[[], None], repeats: bool = False, override: bool = True, group: str = "default") -> None:
        with self._lock:
            g = self._get_group(group)
            if name in g:
                if not override:
                    RBQLog.log(f"⚠️ Timer '{name}' in group '{group}' already exists")
                    return
                g[name].clear()
            timer = GCDStyleTimer(start, interval, callback, repeats, name=f"{group}.{name}")
            g[name] = timer
            timer.fire()

    def remove_timer(self, name: str, group: str = "default") -> None:
        with self._lock:
            g = self._get_group(group)
            timer = g.pop(name, None)
            if timer:
                timer.clear()

    def pause_timer(self, name: str, group: str = "default") -> None:
        with self._lock:
            g = self._get_group(group)
            if name in g:
                g[name].pause()

    def resume_timer(self, name: str, group: str = "default") -> None:
        with self._lock:
            g = self._get_group(group)
            if name in g:
                g[name].resume()

    def update_timer(self, name: str, group: str = "default", **kwargs: Any) -> None:
        with self._lock:
            g = self._get_group(group)
            if name in g:
                g[name].update(**kwargs)

    def list_timers(self, group: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        with self._lock:
            result = {}
            groups = [group] if group else self._timers.keys()
            for g in groups:
                timers = self._timers.get(g, {})
                result[g] = [{
                    'name': name,
                    'is_running': t.is_running(),
                    'is_paused': t.is_paused()
                } for name, t in timers.items()]
            return result

    def clear_group(self, group: str) -> None:
        with self._lock:
            timers = self._timers.get(group, {})
            for t in timers.values():
                t.clear()
            self._timers.pop(group, None)

    def clear_all(self) -> None:
        with self._lock:
            for group in list(self._timers.keys()):
                self.clear_group(group)

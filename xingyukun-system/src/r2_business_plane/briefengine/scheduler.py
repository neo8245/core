"""简报调度器 - 定期与触发式简报调度"""

from typing import Optional, Callable, List
from datetime import datetime, timedelta
from enum import Enum
from src.common.logger import get_logger

logger = get_logger(__name__)


class ScheduleFrequency(str, Enum):
    """调度频率"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    HOURLY = "hourly"


class BriefScheduler:
    """简报调度器"""

    def __init__(self):
        self.schedules: List[dict] = []

    def schedule_brief(
        self,
        name: str,
        frequency: ScheduleFrequency,
        callback: Callable,
        start_time: Optional[datetime] = None,
        is_active: bool = True,
    ) -> dict:
        """调度定期简报"""
        schedule = {
            "id": f"schedule_{len(self.schedules)}_{datetime.utcnow().timestamp()}",
            "name": name,
            "frequency": frequency.value,
            "callback": callback,
            "start_time": start_time or datetime.utcnow(),
            "last_run": None,
            "next_run": self._calculate_next_run(frequency, start_time),
            "is_active": is_active,
        }

        self.schedules.append(schedule)

        logger.info(f"Brief schedule created: {schedule['id']}", {
            "name": name,
            "frequency": frequency.value,
            "next_run": schedule["next_run"].isoformat(),
        })

        return schedule

    def trigger_brief(self, trigger_condition: Callable, callback: Callable) -> bool:
        """触发式简报"""
        if trigger_condition():
            try:
                callback()
                logger.info("Triggered brief executed successfully")
                return True
            except Exception as e:
                logger.error("Triggered brief execution failed", {"error": str(e)})
                return False

        return False

    def _calculate_next_run(
        self,
        frequency: ScheduleFrequency,
        start_time: Optional[datetime] = None,
    ) -> datetime:
        """计算下次运行时间"""
        now = datetime.utcnow()
        base_time = start_time or now

        if frequency == ScheduleFrequency.HOURLY:
            return base_time + timedelta(hours=1)
        elif frequency == ScheduleFrequency.DAILY:
            return base_time + timedelta(days=1)
        elif frequency == ScheduleFrequency.WEEKLY:
            return base_time + timedelta(weeks=1)
        elif frequency == ScheduleFrequency.MONTHLY:
            return base_time + timedelta(days=30)

        return base_time + timedelta(days=1)

from dataclasses import dataclass, field
from datetime import datetime
from collections import deque

from aiogram.types import User

from bot.services.logger import telegram_logger


@dataclass
class UserSession:
    user_id: int
    username: str | None
    start_time: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    actions: deque = field(default_factory=lambda: deque(maxlen=10))
    action_count: int = 0

    def add_action(self, action: str) -> None:
        self.last_activity = datetime.now()
        self.actions.append((datetime.now(), action))
        self.action_count += 1

    def get_duration_seconds(self) -> int:
        return int((self.last_activity - self.start_time).total_seconds())

    def get_last_actions(self) -> list[str]:
        return [action for _, action in self.actions]


class SessionTracker:
    def __init__(self) -> None:
        self._sessions: dict[int, UserSession] = {}

    def get_or_create_session(self, user: User) -> UserSession:
        if user.id not in self._sessions:
            self._sessions[user.id] = UserSession(
                user_id=user.id,
                username=user.username
            )
        return self._sessions[user.id]

    def track_action(self, user: User, action: str) -> None:
        session = self.get_or_create_session(user)
        session.add_action(action)

    async def end_session_and_log(self, user: User) -> None:
        if user.id not in self._sessions:
            return

        session = self._sessions[user.id]
        duration = session.get_duration_seconds()
        actions = session.get_last_actions()

        await telegram_logger.log_session_end(
            user=user,
            duration_seconds=duration,
            action_count=session.action_count,
            last_actions=actions
        )

        del self._sessions[user.id]

    def get_session(self, user_id: int) -> UserSession | None:
        return self._sessions.get(user_id)

    def clear_session(self, user_id: int) -> None:
        if user_id in self._sessions:
            del self._sessions[user_id]


session_tracker = SessionTracker()

"""Supabase implementations of order_tracking repository interfaces.

Single file with all four repos + the realtime no-op. Tables (created via
Supabase migrations; the names match what the use_cases read/write):

  - order_status_history
  - notification_history
  - order_item_tracking
  - order_timeline_events

Realtime broadcasts are no-ops for now — Supabase channels can be plugged
in later without changing the interface.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from supabase import AClient

from ..domain.order_tracking_entities import (
    NotificationHistory,
    OrderItemTracking,
    OrderStatusHistory,
)
from ..domain.order_tracking_enums import (
    NotificationChannel,
    NotificationStatus,
    OrderItemStatus,
)
from ..domain.order_tracking_repos import (
    INotificationHistoryRepository,
    IOrderItemTrackingRepository,
    IOrderStatusHistoryRepository,
    IOrderTimelineRepository,
    IRealtimeEventRepository,
)
from ..domain.order_tracking_vos import KitchenWorkflowStatus, OrderTimeline

logger = logging.getLogger(__name__)


def _ts(value: Optional[str]) -> Optional[datetime]:
    """Parse ISO timestamp from Supabase rows."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


# ──────────────────────────────────────────────────────────────────────────────
# OrderStatusHistory
# ──────────────────────────────────────────────────────────────────────────────

class SupabaseOrderStatusHistoryRepository(IOrderStatusHistoryRepository):
    def __init__(self, client: AClient):
        self._client = client
        self._table = "order_status_history"

    async def create_status_history(self, h: OrderStatusHistory) -> OrderStatusHistory:
        row = {
            "id": str(h.id),
            "order_id": str(h.order_id),
            "status": h.status,
            "previous_status": h.previous_status,
            "changed_by": str(h.changed_by) if h.changed_by else None,
            "changed_at": (h.changed_at or datetime.now(timezone.utc)).isoformat(),
            "estimated_completion_time": h.estimated_completion_time.isoformat() if h.estimated_completion_time else None,
            "actual_completion_time": h.actual_completion_time.isoformat() if h.actual_completion_time else None,
            "preparation_notes": h.preparation_notes,
            "item_statuses": h.item_statuses or {},
            "change_reason": h.change_reason,
            "system_generated": h.system_generated,
        }
        resp = await self._client.table(self._table).insert(row).execute()
        if not resp.data:
            raise RuntimeError("order_status_history insert returned no data")
        return h

    async def get_by_id(self, history_id: UUID) -> Optional[OrderStatusHistory]:
        resp = await self._client.table(self._table).select("*").eq("id", str(history_id)).execute()
        if not resp.data:
            return None
        return self._map(resp.data[0])

    async def get_by_order_id(self, order_id: UUID) -> List[OrderStatusHistory]:
        resp = await (
            self._client.table(self._table)
            .select("*")
            .eq("order_id", str(order_id))
            .order("changed_at", desc=True)
            .execute()
        )
        return [self._map(r) for r in resp.data]

    async def get_latest_by_order_id(self, order_id: UUID) -> Optional[OrderStatusHistory]:
        resp = await (
            self._client.table(self._table)
            .select("*")
            .eq("order_id", str(order_id))
            .order("changed_at", desc=True)
            .limit(1)
            .execute()
        )
        if not resp.data:
            return None
        return self._map(resp.data[0])

    async def get_by_status(self, status: str, restaurant_id: Optional[UUID] = None, limit: int = 100) -> List[OrderStatusHistory]:
        q = self._client.table(self._table).select("*").eq("status", status).limit(limit)
        resp = await q.execute()
        return [self._map(r) for r in resp.data]

    async def get_by_date_range(self, start_date: datetime, end_date: datetime, restaurant_id: Optional[UUID] = None) -> List[OrderStatusHistory]:
        q = (
            self._client.table(self._table)
            .select("*")
            .gte("changed_at", start_date.isoformat())
            .lte("changed_at", end_date.isoformat())
        )
        resp = await q.execute()
        return [self._map(r) for r in resp.data]

    async def update_status_history(self, h: OrderStatusHistory) -> OrderStatusHistory:
        updates = {
            "status": h.status,
            "preparation_notes": h.preparation_notes,
            "item_statuses": h.item_statuses or {},
            "actual_completion_time": h.actual_completion_time.isoformat() if h.actual_completion_time else None,
        }
        await self._client.table(self._table).update(updates).eq("id", str(h.id)).execute()
        return h

    async def delete_status_history(self, history_id: UUID) -> bool:
        resp = await self._client.table(self._table).delete().eq("id", str(history_id)).execute()
        return len(resp.data) > 0

    @staticmethod
    def _map(row: Dict[str, Any]) -> OrderStatusHistory:
        return OrderStatusHistory(
            id=UUID(row["id"]),
            order_id=UUID(row["order_id"]),
            status=row["status"],
            previous_status=row.get("previous_status"),
            changed_by=UUID(row["changed_by"]) if row.get("changed_by") else None,
            changed_at=_ts(row.get("changed_at")) or datetime.now(timezone.utc),
            estimated_completion_time=_ts(row.get("estimated_completion_time")),
            actual_completion_time=_ts(row.get("actual_completion_time")),
            preparation_notes=row.get("preparation_notes"),
            item_statuses=row.get("item_statuses") or {},
            change_reason=row.get("change_reason"),
            system_generated=bool(row.get("system_generated", False)),
            created_at=_ts(row.get("created_at")),
        )


# ──────────────────────────────────────────────────────────────────────────────
# NotificationHistory
# ──────────────────────────────────────────────────────────────────────────────

class SupabaseNotificationHistoryRepository(INotificationHistoryRepository):
    def __init__(self, client: AClient):
        self._client = client
        self._table = "notification_history"

    async def create_notification_history(self, n: NotificationHistory) -> NotificationHistory:
        row = {
            "id": str(n.id),
            "order_id": str(n.order_id),
            "restaurant_id": str(n.restaurant_id),
            "channel": n.channel.value,
            "recipient": n.recipient,
            "subject": n.subject,
            "message_content": n.message_content,
            "status": n.status.value,
            "sent_at": n.sent_at.isoformat() if n.sent_at else None,
            "delivered_at": n.delivered_at.isoformat() if n.delivered_at else None,
            "opened_at": n.opened_at.isoformat() if n.opened_at else None,
            "clicked_at": n.clicked_at.isoformat() if n.clicked_at else None,
            "error_message": n.error_message,
            "retry_count": n.retry_count,
            "max_retries": n.max_retries,
            "external_message_id": n.external_message_id,
            "external_status": n.external_status,
            "cost_amount": float(n.cost_amount) if n.cost_amount is not None else None,
            "cost_currency": n.cost_currency,
        }
        resp = await self._client.table(self._table).insert(row).execute()
        if not resp.data:
            raise RuntimeError("notification_history insert returned no data")
        return n

    async def get_by_id(self, notification_id: UUID) -> Optional[NotificationHistory]:
        resp = await self._client.table(self._table).select("*").eq("id", str(notification_id)).execute()
        if not resp.data:
            return None
        return self._map(resp.data[0])

    async def get_by_order_id(self, order_id: UUID) -> List[NotificationHistory]:
        resp = await (
            self._client.table(self._table)
            .select("*")
            .eq("order_id", str(order_id))
            .order("created_at", desc=True)
            .execute()
        )
        return [self._map(r) for r in resp.data]

    async def get_by_channel_and_recipient(
        self,
        channel: NotificationChannel,
        recipient: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[NotificationHistory]:
        q = (
            self._client.table(self._table)
            .select("*")
            .eq("channel", channel.value)
            .eq("recipient", recipient)
        )
        if start_date:
            q = q.gte("created_at", start_date.isoformat())
        if end_date:
            q = q.lte("created_at", end_date.isoformat())
        resp = await q.execute()
        return [self._map(r) for r in resp.data]

    async def get_pending_notifications(self, max_retries: int = 3) -> List[NotificationHistory]:
        resp = await (
            self._client.table(self._table)
            .select("*")
            .eq("status", NotificationStatus.PENDING.value)
            .lt("retry_count", max_retries)
            .execute()
        )
        return [self._map(r) for r in resp.data]

    async def get_failed_notifications(self, retry_eligible_only: bool = True) -> List[NotificationHistory]:
        q = self._client.table(self._table).select("*").eq("status", NotificationStatus.FAILED.value)
        if retry_eligible_only:
            q = q.lt("retry_count", 3)
        resp = await q.execute()
        return [self._map(r) for r in resp.data]

    async def update_notification_history(self, n: NotificationHistory) -> NotificationHistory:
        updates = {
            "status": n.status.value,
            "sent_at": n.sent_at.isoformat() if n.sent_at else None,
            "delivered_at": n.delivered_at.isoformat() if n.delivered_at else None,
            "opened_at": n.opened_at.isoformat() if n.opened_at else None,
            "clicked_at": n.clicked_at.isoformat() if n.clicked_at else None,
            "error_message": n.error_message,
            "retry_count": n.retry_count,
            "external_message_id": n.external_message_id,
            "external_status": n.external_status,
        }
        await self._client.table(self._table).update(updates).eq("id", str(n.id)).execute()
        return n

    async def get_delivery_metrics(
        self, restaurant_id: UUID, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        # Cheap aggregate — caller can refine later. Returns safe defaults.
        resp = await (
            self._client.table(self._table)
            .select("id,status,channel,cost_amount")
            .eq("restaurant_id", str(restaurant_id))
            .gte("created_at", start_date.isoformat())
            .lte("created_at", end_date.isoformat())
            .execute()
        )
        rows = resp.data or []
        total = len(rows)
        delivered = sum(1 for r in rows if r.get("status") == NotificationStatus.DELIVERED.value)
        return {
            "total_notifications": total,
            "delivered": delivered,
            "failed": sum(1 for r in rows if r.get("status") == NotificationStatus.FAILED.value),
            "delivery_success_rate": (delivered / total) if total else 0.0,
        }

    @staticmethod
    def _map(row: Dict[str, Any]) -> NotificationHistory:
        return NotificationHistory(
            id=UUID(row["id"]),
            order_id=UUID(row["order_id"]),
            restaurant_id=UUID(row["restaurant_id"]),
            channel=NotificationChannel(row["channel"]),
            recipient=row["recipient"],
            subject=row.get("subject"),
            message_content=row.get("message_content", ""),
            status=NotificationStatus(row["status"]),
            sent_at=_ts(row.get("sent_at")),
            delivered_at=_ts(row.get("delivered_at")),
            opened_at=_ts(row.get("opened_at")),
            clicked_at=_ts(row.get("clicked_at")),
            error_message=row.get("error_message"),
            retry_count=int(row.get("retry_count", 0)),
            max_retries=int(row.get("max_retries", 3)),
            external_message_id=row.get("external_message_id"),
            external_status=row.get("external_status"),
            cost_amount=row.get("cost_amount"),
            cost_currency=row.get("cost_currency", "INR"),
            created_at=_ts(row.get("created_at")),
        )


# ──────────────────────────────────────────────────────────────────────────────
# OrderItemTracking
# ──────────────────────────────────────────────────────────────────────────────

class SupabaseOrderItemTrackingRepository(IOrderItemTrackingRepository):
    def __init__(self, client: AClient):
        self._client = client
        # Schema has `order_item_status_history` (migration 20250929000000)
        self._table = "order_item_status_history"

    async def create_item_tracking(self, t: OrderItemTracking) -> OrderItemTracking:
        row = {
            "id": str(t.id),
            "order_id": str(t.order_id),
            "order_item_id": str(t.order_item_id),
            "status": t.status.value,
            "previous_status": t.previous_status.value if t.previous_status else None,
            "assigned_to": str(t.assigned_to) if t.assigned_to else None,
            "estimated_ready_time": t.estimated_ready_time.isoformat() if t.estimated_ready_time else None,
            "actual_ready_time": t.actual_ready_time.isoformat() if t.actual_ready_time else None,
            "preparation_notes": t.preparation_notes,
            "quality_check_passed": t.quality_check_passed,
            "quality_notes": t.quality_notes,
            "changed_by": str(t.changed_by) if t.changed_by else None,
            "changed_at": (t.changed_at or datetime.now(timezone.utc)).isoformat(),
        }
        resp = await self._client.table(self._table).insert(row).execute()
        if not resp.data:
            raise RuntimeError("order_item_tracking insert returned no data")
        return t

    async def get_by_id(self, tracking_id: UUID) -> Optional[OrderItemTracking]:
        resp = await self._client.table(self._table).select("*").eq("id", str(tracking_id)).execute()
        if not resp.data:
            return None
        return self._map(resp.data[0])

    async def get_by_order_id(self, order_id: UUID) -> List[OrderItemTracking]:
        resp = await (
            self._client.table(self._table)
            .select("*")
            .eq("order_id", str(order_id))
            .order("changed_at", desc=True)
            .execute()
        )
        return [self._map(r) for r in resp.data]

    async def get_by_order_item_id(self, order_item_id: UUID) -> List[OrderItemTracking]:
        resp = await (
            self._client.table(self._table)
            .select("*")
            .eq("order_item_id", str(order_item_id))
            .order("changed_at", desc=True)
            .execute()
        )
        return [self._map(r) for r in resp.data]

    async def get_by_status(
        self,
        status: OrderItemStatus,
        restaurant_id: Optional[UUID] = None,
        assigned_to: Optional[UUID] = None,
    ) -> List[OrderItemTracking]:
        q = self._client.table(self._table).select("*").eq("status", status.value)
        if assigned_to:
            q = q.eq("assigned_to", str(assigned_to))
        resp = await q.execute()
        return [self._map(r) for r in resp.data]

    async def get_assigned_to_staff(self, staff_id: UUID) -> List[OrderItemTracking]:
        resp = await (
            self._client.table(self._table)
            .select("*")
            .eq("assigned_to", str(staff_id))
            .execute()
        )
        return [self._map(r) for r in resp.data]

    async def update_item_tracking(self, t: OrderItemTracking) -> OrderItemTracking:
        updates = {
            "status": t.status.value,
            "previous_status": t.previous_status.value if t.previous_status else None,
            "assigned_to": str(t.assigned_to) if t.assigned_to else None,
            "estimated_ready_time": t.estimated_ready_time.isoformat() if t.estimated_ready_time else None,
            "actual_ready_time": t.actual_ready_time.isoformat() if t.actual_ready_time else None,
            "preparation_notes": t.preparation_notes,
            "quality_check_passed": t.quality_check_passed,
            "quality_notes": t.quality_notes,
            "changed_by": str(t.changed_by) if t.changed_by else None,
            "changed_at": (t.changed_at or datetime.now(timezone.utc)).isoformat(),
        }
        await self._client.table(self._table).update(updates).eq("id", str(t.id)).execute()
        return t

    async def get_kitchen_workflow_status(self, order_id: UUID) -> Optional[KitchenWorkflowStatus]:
        # Aggregate item statuses for the order into a workflow VO
        items = await self.get_by_order_id(order_id)
        if not items:
            return None
        pending = sum(1 for i in items if i.status == OrderItemStatus.PENDING)
        preparing = sum(1 for i in items if i.status == OrderItemStatus.PREPARING)
        ready = sum(1 for i in items if i.status == OrderItemStatus.READY)
        served = sum(1 for i in items if i.status == OrderItemStatus.SERVED)
        return KitchenWorkflowStatus.from_item_counts(
            order_id=order_id,
            items_pending=pending,
            items_preparing=preparing,
            items_ready=ready,
            items_served=served,
        )

    @staticmethod
    def _map(row: Dict[str, Any]) -> OrderItemTracking:
        prev = row.get("previous_status")
        return OrderItemTracking(
            id=UUID(row["id"]),
            order_id=UUID(row["order_id"]),
            order_item_id=UUID(row["order_item_id"]),
            status=OrderItemStatus(row["status"]),
            previous_status=OrderItemStatus(prev) if prev else None,
            assigned_to=UUID(row["assigned_to"]) if row.get("assigned_to") else None,
            estimated_ready_time=_ts(row.get("estimated_ready_time")),
            actual_ready_time=_ts(row.get("actual_ready_time")),
            preparation_notes=row.get("preparation_notes"),
            quality_check_passed=row.get("quality_check_passed"),
            quality_notes=row.get("quality_notes"),
            changed_by=UUID(row["changed_by"]) if row.get("changed_by") else None,
            changed_at=_ts(row.get("changed_at")),
            created_at=_ts(row.get("created_at")),
        )


# ──────────────────────────────────────────────────────────────────────────────
# OrderTimeline
# ──────────────────────────────────────────────────────────────────────────────

class SupabaseOrderTimelineRepository(IOrderTimelineRepository):
    def __init__(self, client: AClient):
        self._client = client
        # No dedicated timeline table in the schema. Returns empty timeline
        # and ignores inserts — order_status_history is the source of truth.
        self._table = "order_status_history"

    async def get_order_timeline(self, order_id: UUID) -> Optional[OrderTimeline]:
        # Derive a minimal timeline from order_status_history (status changes only).
        resp = await (
            self._client.table(self._table)
            .select("id,status,previous_status,change_reason,changed_at")
            .eq("order_id", str(order_id))
            .order("changed_at", desc=False)
            .execute()
        )
        if not resp.data:
            return None
        events = [
            {
                "id": r.get("id"),
                "event_type": f"status:{r.get('status')}",
                "title": f"Status: {r.get('status')}",
                "description": r.get("change_reason") or "",
                "metadata": {"previous_status": r.get("previous_status")},
                "created_at": r.get("changed_at"),
            }
            for r in resp.data
        ]
        first = _ts(resp.data[0].get("changed_at")) or datetime.now(timezone.utc)
        last = _ts(resp.data[-1].get("changed_at")) or datetime.now(timezone.utc)
        return OrderTimeline.from_partial(
            order_id=order_id,
            events=events,
            created_at=first,
            last_updated=last,
        )

    async def add_timeline_event(
        self,
        order_id: UUID,
        event_type: str,
        title: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> OrderTimeline:
        # No-op: no timeline table. Status changes are auto-logged via DB trigger.
        existing = await self.get_order_timeline(order_id)
        if existing:
            return existing
        return OrderTimeline.from_partial(
            order_id=order_id,
            events=[],
            created_at=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc),
        )

    async def get_timeline_events_by_type(self, order_id: UUID, event_type: str) -> List[Dict[str, Any]]:
        # Map "event_type" to status changes for backward-compat reads.
        if event_type.startswith("status:"):
            target = event_type.split(":", 1)[1]
            resp = await (
                self._client.table(self._table)
                .select("id,status,previous_status,change_reason,changed_at")
                .eq("order_id", str(order_id))
                .eq("status", target)
                .order("changed_at", desc=True)
                .execute()
            )
        else:
            resp = await (
                self._client.table(self._table)
                .select("id,status,previous_status,change_reason,changed_at")
                .eq("order_id", str(order_id))
                .order("changed_at", desc=True)
                .execute()
            )
        return resp.data or []


# ──────────────────────────────────────────────────────────────────────────────
# RealtimeEvent — no-op for now; hook Supabase channels later
# ──────────────────────────────────────────────────────────────────────────────

class NoopRealtimeEventRepository(IRealtimeEventRepository):
    async def broadcast_order_status_update(self, **kwargs) -> bool:
        return True

    async def broadcast_item_status_update(self, **kwargs) -> bool:
        return True

    async def broadcast_eta_update(self, **kwargs) -> bool:
        return True

    async def broadcast_notification_sent(self, **kwargs) -> bool:
        return True

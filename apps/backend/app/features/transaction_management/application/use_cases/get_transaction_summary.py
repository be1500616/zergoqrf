"""Get Transaction Summary Use Case.

This module implements the use case for retrieving transaction summaries
and analytics for restaurant financial dashboards.
"""

import logging
from datetime import date, datetime, timedelta
from typing import Optional, List
from uuid import UUID

from ...domain.transaction_repos import ITransactionRepository
from ...domain.transaction_exceptions import TransactionError
from ..transaction_dtos import (
    TransactionSummaryDTO,
    PaymentMethodBreakdownDTO,
    DailyRevenueTrendDTO,
)

logger = logging.getLogger(__name__)


class GetTransactionSummaryUseCase:
    """Use case for retrieving transaction summaries and analytics.
    
    This use case provides comprehensive transaction analytics including
    summaries, payment method breakdowns, and revenue trends for dashboards.
    """
    
    def __init__(self, transaction_repository: ITransactionRepository):
        """Initialize the get transaction summary use case.
        
        Args:
            transaction_repository: Repository for transaction operations
        """
        self._transaction_repo = transaction_repository
    
    async def execute(
        self,
        restaurant_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        period: str = "monthly"
    ) -> TransactionSummaryDTO:
        """Execute the get transaction summary use case.
        
        Args:
            restaurant_id: Restaurant identifier
            start_date: Summary start date (optional)
            end_date: Summary end date (optional)
            period: Summary period (daily, weekly, monthly)
            
        Returns:
            Transaction summary data
            
        Raises:
            TransactionError: If summary retrieval fails
        """
        try:
            logger.info(
                "Retrieving transaction summary for restaurant %s",
                restaurant_id,
                extra={
                    "restaurant_id": str(restaurant_id),
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None,
                    "period": period,
                }
            )
            
            # Set default date range if not provided
            if not start_date or not end_date:
                start_date, end_date = self._get_default_date_range(period)
            
            # Validate date range
            self._validate_date_range(start_date, end_date)
            
            # Get transaction summary from repository
            summary_data = await self._transaction_repo.get_transaction_summary(
                restaurant_id=restaurant_id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Map to DTO
            summary_dto = TransactionSummaryDTO(
                total_transactions=summary_data.get("total_transactions", 0),
                total_amount=summary_data.get("total_amount", 0),
                completed_transactions=summary_data.get("completed_transactions", 0),
                completed_amount=summary_data.get("completed_amount", 0),
                pending_transactions=summary_data.get("pending_transactions", 0),
                pending_amount=summary_data.get("pending_amount", 0),
                failed_transactions=summary_data.get("failed_transactions", 0),
                failed_amount=summary_data.get("failed_amount", 0),
                refunded_transactions=summary_data.get("refunded_transactions", 0),
                refunded_amount=summary_data.get("refunded_amount", 0),
                average_transaction_amount=summary_data.get("average_transaction_amount", 0),
            )
            
            logger.info(
                "Transaction summary retrieved successfully",
                extra={
                    "restaurant_id": str(restaurant_id),
                    "total_transactions": summary_dto.total_transactions,
                    "total_amount": float(summary_dto.total_amount),
                }
            )
            
            return summary_dto
            
        except Exception as e:
            logger.error(
                "Failed to retrieve transaction summary",
                extra={
                    "restaurant_id": str(restaurant_id),
                    "error": str(e),
                },
                exc_info=True
            )
            raise TransactionError(f"Failed to retrieve transaction summary: {str(e)}")
    
    async def get_payment_method_breakdown(
        self,
        restaurant_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[PaymentMethodBreakdownDTO]:
        """Get payment method breakdown for a restaurant.
        
        Args:
            restaurant_id: Restaurant identifier
            start_date: Analysis start date
            end_date: Analysis end date
            
        Returns:
            List of payment method breakdown data
        """
        try:
            logger.info(
                "Retrieving payment method breakdown for restaurant %s",
                restaurant_id,
                extra={"restaurant_id": str(restaurant_id)}
            )
            
            # Set default date range if not provided
            if not start_date or not end_date:
                start_date, end_date = self._get_default_date_range("monthly")
            
            # Get breakdown data from repository
            breakdown_data = await self._transaction_repo.get_payment_method_breakdown(
                restaurant_id=restaurant_id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Map to DTOs
            breakdown_dtos = [
                PaymentMethodBreakdownDTO(
                    payment_method=item["payment_method"],
                    transaction_count=item["transaction_count"],
                    total_amount=item["total_amount"],
                    percentage=item["percentage"]
                )
                for item in breakdown_data
            ]
            
            logger.info(
                "Payment method breakdown retrieved successfully",
                extra={
                    "restaurant_id": str(restaurant_id),
                    "methods_count": len(breakdown_dtos),
                }
            )
            
            return breakdown_dtos
            
        except Exception as e:
            logger.error(
                "Failed to retrieve payment method breakdown",
                extra={
                    "restaurant_id": str(restaurant_id),
                    "error": str(e),
                },
                exc_info=True
            )
            raise TransactionError(f"Failed to retrieve payment method breakdown: {str(e)}")
    
    async def get_daily_revenue_trends(
        self,
        restaurant_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        days: int = 30
    ) -> List[DailyRevenueTrendDTO]:
        """Get daily revenue trends for a restaurant.
        
        Args:
            restaurant_id: Restaurant identifier
            start_date: Trend start date
            end_date: Trend end date
            days: Number of days to include (if dates not provided)
            
        Returns:
            List of daily revenue trend data
        """
        try:
            logger.info(
                "Retrieving daily revenue trends for restaurant %s",
                restaurant_id,
                extra={"restaurant_id": str(restaurant_id)}
            )
            
            # Set default date range if not provided
            if not start_date or not end_date:
                end_date = date.today()
                start_date = end_date - timedelta(days=days - 1)
            
            # Get trend data from repository
            trend_data = await self._transaction_repo.get_daily_revenue_trends(
                restaurant_id=restaurant_id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Map to DTOs
            trend_dtos = [
                DailyRevenueTrendDTO(
                    transaction_date=item["transaction_date"],
                    transaction_count=item["transaction_count"],
                    total_revenue=item["total_revenue"],
                    completed_revenue=item["completed_revenue"],
                    refunded_amount=item["refunded_amount"],
                    net_revenue=item["net_revenue"]
                )
                for item in trend_data
            ]
            
            logger.info(
                "Daily revenue trends retrieved successfully",
                extra={
                    "restaurant_id": str(restaurant_id),
                    "days_count": len(trend_dtos),
                }
            )
            
            return trend_dtos
            
        except Exception as e:
            logger.error(
                "Failed to retrieve daily revenue trends",
                extra={
                    "restaurant_id": str(restaurant_id),
                    "error": str(e),
                },
                exc_info=True
            )
            raise TransactionError(f"Failed to retrieve daily revenue trends: {str(e)}")
    
    def _get_default_date_range(self, period: str) -> tuple[date, date]:
        """Get default date range based on period.
        
        Args:
            period: Period type (daily, weekly, monthly)
            
        Returns:
            Tuple of (start_date, end_date)
        """
        end_date = date.today()
        
        if period == "daily":
            start_date = end_date
        elif period == "weekly":
            start_date = end_date - timedelta(days=7)
        elif period == "monthly":
            start_date = end_date - timedelta(days=30)
        else:
            # Default to monthly
            start_date = end_date - timedelta(days=30)
        
        return start_date, end_date
    
    def _validate_date_range(self, start_date: date, end_date: date) -> None:
        """Validate date range parameters.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Raises:
            ValueError: If date range is invalid
        """
        if start_date > end_date:
            raise ValueError("Start date must be before or equal to end date")
        
        if end_date > date.today():
            raise ValueError("End date cannot be in the future")
        
        # Limit to maximum 1 year range
        max_days = 365
        if (end_date - start_date).days > max_days:
            raise ValueError(f"Date range cannot exceed {max_days} days")

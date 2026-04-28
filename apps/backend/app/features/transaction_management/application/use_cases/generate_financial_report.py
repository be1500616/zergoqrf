"""Generate Financial Report Use Case.

This module implements the use case for generating financial reports
with comprehensive analytics and export capabilities.
"""

import logging
from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal

from ...domain.transaction_repos import ITransactionRepository, IRefundRepository, IPayoutRepository
from ...domain.transaction_exceptions import TransactionError
from ..transaction_dtos import (
    FinancialReportDTO,
    TransactionSummaryDTO,
    PaymentMethodBreakdownDTO,
    DailyRevenueTrendDTO,
    RefundSummaryDTO,
    PayoutSummaryDTO,
)

logger = logging.getLogger(__name__)


class GenerateFinancialReportUseCase:
    """Use case for generating comprehensive financial reports.
    
    This use case provides detailed financial reporting including transaction
    summaries, payment method breakdowns, revenue trends, and export capabilities.
    """
    
    def __init__(
        self,
        transaction_repository: ITransactionRepository,
        refund_repository: IRefundRepository,
        payout_repository: IPayoutRepository,
    ):
        """Initialize the generate financial report use case.
        
        Args:
            transaction_repository: Repository for transaction operations
            refund_repository: Repository for refund operations
            payout_repository: Repository for payout operations
        """
        self._transaction_repo = transaction_repository
        self._refund_repo = refund_repository
        self._payout_repo = payout_repository
    
    async def execute(
        self,
        restaurant_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        report_type: str = "comprehensive",
        include_trends: bool = True,
        include_breakdowns: bool = True
    ) -> FinancialReportDTO:
        """Execute the generate financial report use case.
        
        Args:
            restaurant_id: Restaurant identifier
            start_date: Report start date (optional)
            end_date: Report end date (optional)
            report_type: Type of report (comprehensive, summary, detailed)
            include_trends: Whether to include revenue trends
            include_breakdowns: Whether to include payment method breakdowns
            
        Returns:
            Financial report data
            
        Raises:
            TransactionError: If report generation fails
        """
        try:
            logger.info(
                "Generating financial report for restaurant %s",
                restaurant_id,
                extra={
                    "restaurant_id": str(restaurant_id),
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None,
                    "report_type": report_type,
                    "include_trends": include_trends,
                    "include_breakdowns": include_breakdowns,
                }
            )
            
            # Set default date range if not provided
            if not start_date or not end_date:
                start_date, end_date = self._get_default_date_range()
            
            # Validate date range
            self._validate_date_range(start_date, end_date)
            
            # Generate report components
            report_data = await self._generate_report_data(
                restaurant_id,
                start_date,
                end_date,
                report_type,
                include_trends,
                include_breakdowns
            )
            
            logger.info(
                "Financial report generated successfully",
                extra={
                    "restaurant_id": str(restaurant_id),
                    "report_period": f"{start_date} to {end_date}",
                    "total_transactions": report_data.transaction_summary.total_transactions,
                    "total_revenue": float(report_data.transaction_summary.total_amount),
                }
            )
            
            return report_data
            
        except Exception as e:
            logger.error(
                "Failed to generate financial report",
                extra={
                    "restaurant_id": str(restaurant_id),
                    "error": str(e),
                },
                exc_info=True
            )
            raise TransactionError(f"Failed to generate financial report: {str(e)}")
    
    async def generate_daily_report(
        self,
        restaurant_id: UUID,
        report_date: Optional[date] = None
    ) -> FinancialReportDTO:
        """Generate daily financial report.
        
        Args:
            restaurant_id: Restaurant identifier
            report_date: Date for the report (defaults to today)
            
        Returns:
            Daily financial report
        """
        if not report_date:
            report_date = date.today()
        
        return await self.execute(
            restaurant_id=restaurant_id,
            start_date=report_date,
            end_date=report_date,
            report_type="daily",
            include_trends=False,
            include_breakdowns=True
        )
    
    async def generate_monthly_report(
        self,
        restaurant_id: UUID,
        year: Optional[int] = None,
        month: Optional[int] = None
    ) -> FinancialReportDTO:
        """Generate monthly financial report.
        
        Args:
            restaurant_id: Restaurant identifier
            year: Year for the report (defaults to current year)
            month: Month for the report (defaults to current month)
            
        Returns:
            Monthly financial report
        """
        if not year or not month:
            today = date.today()
            year = year or today.year
            month = month or today.month
        
        # Calculate month start and end dates
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        return await self.execute(
            restaurant_id=restaurant_id,
            start_date=start_date,
            end_date=end_date,
            report_type="monthly",
            include_trends=True,
            include_breakdowns=True
        )
    
    async def _generate_report_data(
        self,
        restaurant_id: UUID,
        start_date: date,
        end_date: date,
        report_type: str,
        include_trends: bool,
        include_breakdowns: bool
    ) -> FinancialReportDTO:
        """Generate comprehensive report data.
        
        Args:
            restaurant_id: Restaurant identifier
            start_date: Report start date
            end_date: Report end date
            report_type: Type of report
            include_trends: Whether to include trends
            include_breakdowns: Whether to include breakdowns
            
        Returns:
            Financial report DTO
        """
        # Get transaction summary
        transaction_summary = await self._get_transaction_summary(
            restaurant_id, start_date, end_date
        )
        
        # Get refund summary
        refund_summary = await self._get_refund_summary(
            restaurant_id, start_date, end_date
        )
        
        # Get payout summary
        payout_summary = await self._get_payout_summary(
            restaurant_id, start_date, end_date
        )
        
        # Get payment method breakdown if requested
        payment_method_breakdown = None
        if include_breakdowns:
            payment_method_breakdown = await self._get_payment_method_breakdown(
                restaurant_id, start_date, end_date
            )
        
        # Get revenue trends if requested
        revenue_trends = None
        if include_trends:
            revenue_trends = await self._get_revenue_trends(
                restaurant_id, start_date, end_date
            )
        
        # Calculate key metrics
        net_revenue = (
            transaction_summary.completed_amount - 
            refund_summary.total_refunded_amount
        )
        
        return FinancialReportDTO(
            restaurant_id=restaurant_id,
            report_period_start=start_date,
            report_period_end=end_date,
            report_type=report_type,
            generated_at=datetime.utcnow(),
            transaction_summary=transaction_summary,
            refund_summary=refund_summary,
            payout_summary=payout_summary,
            payment_method_breakdown=payment_method_breakdown,
            revenue_trends=revenue_trends,
            key_metrics={
                "net_revenue": float(net_revenue),
                "gross_revenue": float(transaction_summary.completed_amount),
                "total_refunds": float(refund_summary.total_refunded_amount),
                "average_transaction_value": float(transaction_summary.average_transaction_amount),
                "refund_rate": float(
                    (refund_summary.total_refunds / transaction_summary.total_transactions * 100)
                    if transaction_summary.total_transactions > 0 else 0
                ),
                "completion_rate": float(
                    (transaction_summary.completed_transactions / transaction_summary.total_transactions * 100)
                    if transaction_summary.total_transactions > 0 else 0
                ),
            }
        )
    
    async def _get_transaction_summary(
        self, restaurant_id: UUID, start_date: date, end_date: date
    ) -> TransactionSummaryDTO:
        """Get transaction summary for the period."""
        summary_data = await self._transaction_repo.get_transaction_summary(
            restaurant_id=restaurant_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return TransactionSummaryDTO(
            total_transactions=summary_data.get("total_transactions", 0),
            total_amount=summary_data.get("total_amount", Decimal("0")),
            completed_transactions=summary_data.get("completed_transactions", 0),
            completed_amount=summary_data.get("completed_amount", Decimal("0")),
            pending_transactions=summary_data.get("pending_transactions", 0),
            pending_amount=summary_data.get("pending_amount", Decimal("0")),
            failed_transactions=summary_data.get("failed_transactions", 0),
            failed_amount=summary_data.get("failed_amount", Decimal("0")),
            refunded_transactions=summary_data.get("refunded_transactions", 0),
            refunded_amount=summary_data.get("refunded_amount", Decimal("0")),
            average_transaction_amount=summary_data.get("average_transaction_amount", Decimal("0")),
        )
    
    async def _get_refund_summary(
        self, restaurant_id: UUID, start_date: date, end_date: date
    ) -> RefundSummaryDTO:
        """Get refund summary for the period."""
        refund_data = await self._refund_repo.get_refund_summary(
            restaurant_id=restaurant_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return RefundSummaryDTO(
            total_refunds=refund_data.get("total_refunds", 0),
            total_refunded_amount=refund_data.get("total_refunded_amount", Decimal("0")),
            completed_refunds=refund_data.get("completed_refunds", 0),
            completed_refunded_amount=refund_data.get("completed_refunded_amount", Decimal("0")),
            pending_refunds=refund_data.get("pending_refunds", 0),
            pending_refunded_amount=refund_data.get("pending_refunded_amount", Decimal("0")),
            average_refund_amount=refund_data.get("average_refund_amount", Decimal("0")),
        )
    
    async def _get_payout_summary(
        self, restaurant_id: UUID, start_date: date, end_date: date
    ) -> PayoutSummaryDTO:
        """Get payout summary for the period."""
        payout_data = await self._payout_repo.get_payout_summary(
            restaurant_id=restaurant_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return PayoutSummaryDTO(
            total_payouts=payout_data.get("total_payouts", 0),
            total_payout_amount=payout_data.get("total_payout_amount", Decimal("0")),
            completed_payouts=payout_data.get("completed_payouts", 0),
            completed_payout_amount=payout_data.get("completed_payout_amount", Decimal("0")),
            pending_payouts=payout_data.get("pending_payouts", 0),
            pending_payout_amount=payout_data.get("pending_payout_amount", Decimal("0")),
            total_fees=payout_data.get("total_fees", Decimal("0")),
        )
    
    async def _get_payment_method_breakdown(
        self, restaurant_id: UUID, start_date: date, end_date: date
    ) -> List[PaymentMethodBreakdownDTO]:
        """Get payment method breakdown for the period."""
        breakdown_data = await self._transaction_repo.get_payment_method_breakdown(
            restaurant_id=restaurant_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return [
            PaymentMethodBreakdownDTO(
                payment_method=item["payment_method"],
                transaction_count=item["transaction_count"],
                total_amount=item["total_amount"],
                percentage=item["percentage"]
            )
            for item in breakdown_data
        ]
    
    async def _get_revenue_trends(
        self, restaurant_id: UUID, start_date: date, end_date: date
    ) -> List[DailyRevenueTrendDTO]:
        """Get daily revenue trends for the period."""
        trend_data = await self._transaction_repo.get_daily_revenue_trends(
            restaurant_id=restaurant_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return [
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
    
    def _get_default_date_range(self) -> tuple[date, date]:
        """Get default date range (last 30 days)."""
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        return start_date, end_date
    
    def _validate_date_range(self, start_date: date, end_date: date) -> None:
        """Validate date range parameters."""
        if start_date > end_date:
            raise ValueError("Start date must be before or equal to end date")
        
        if end_date > date.today():
            raise ValueError("End date cannot be in the future")
        
        # Limit to maximum 1 year range
        max_days = 365
        if (end_date - start_date).days > max_days:
            raise ValueError(f"Date range cannot exceed {max_days} days")

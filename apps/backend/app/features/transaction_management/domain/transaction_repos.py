"""Transaction Management Repository Interfaces.

This module defines the repository interfaces for transaction management
following the Repository pattern and Dependency Inversion Principle.
"""

from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from .transaction_entities import Transaction, Refund, Payout
from .transaction_vos import TransactionStatus, RefundStatus, PayoutStatus, PaymentMethod


class ITransactionRepository(ABC):
    """Repository interface for transaction operations.
    
    This interface defines the contract for transaction data access operations
    without coupling to specific database implementations.
    """
    
    @abstractmethod
    async def create_transaction(self, transaction: Transaction) -> Transaction:
        """Create a new transaction.
        
        Args:
            transaction: Transaction entity to create
            
        Returns:
            Created transaction with generated ID and timestamps
            
        Raises:
            TransactionCreationError: If creation fails
        """
        pass
    
    @abstractmethod
    async def get_transaction_by_id(self, transaction_id: UUID) -> Optional[Transaction]:
        """Get transaction by ID.
        
        Args:
            transaction_id: Transaction identifier
            
        Returns:
            Transaction entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_transaction_by_number(self, transaction_number: str) -> Optional[Transaction]:
        """Get transaction by transaction number.
        
        Args:
            transaction_number: Human-readable transaction number
            
        Returns:
            Transaction entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_transactions_by_restaurant(
        self,
        restaurant_id: UUID,
        limit: int = 50,
        offset: int = 0,
        status: Optional[TransactionStatus] = None,
        payment_method: Optional[PaymentMethod] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        search_term: Optional[str] = None
    ) -> List[Transaction]:
        """Get transactions for a restaurant with filtering and pagination.
        
        Args:
            restaurant_id: Restaurant identifier
            limit: Maximum number of transactions to return
            offset: Number of transactions to skip
            status: Filter by transaction status
            payment_method: Filter by payment method
            start_date: Filter by start date
            end_date: Filter by end date
            search_term: Search term for transaction details
            
        Returns:
            List of transaction entities
        """
        pass
    
    @abstractmethod
    async def update_transaction(self, transaction: Transaction) -> Transaction:
        """Update an existing transaction.
        
        Args:
            transaction: Transaction entity with updates
            
        Returns:
            Updated transaction entity
            
        Raises:
            TransactionNotFoundError: If transaction doesn't exist
            TransactionUpdateError: If update fails
        """
        pass
    
    @abstractmethod
    async def get_transaction_summary(
        self,
        restaurant_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get transaction summary for a restaurant.
        
        Args:
            restaurant_id: Restaurant identifier
            start_date: Summary start date
            end_date: Summary end date
            
        Returns:
            Dictionary with transaction summary data
        """
        pass
    
    @abstractmethod
    async def get_payment_method_breakdown(
        self,
        restaurant_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """Get payment method breakdown for a restaurant.
        
        Args:
            restaurant_id: Restaurant identifier
            start_date: Analysis start date
            end_date: Analysis end date
            
        Returns:
            List of payment method statistics
        """
        pass
    
    @abstractmethod
    async def get_daily_revenue_trends(
        self,
        restaurant_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """Get daily revenue trends for a restaurant.
        
        Args:
            restaurant_id: Restaurant identifier
            start_date: Trend start date
            end_date: Trend end date
            
        Returns:
            List of daily revenue data
        """
        pass


class IRefundRepository(ABC):
    """Repository interface for refund operations."""
    
    @abstractmethod
    async def create_refund(self, refund: Refund) -> Refund:
        """Create a new refund.
        
        Args:
            refund: Refund entity to create
            
        Returns:
            Created refund with generated ID and timestamps
            
        Raises:
            RefundCreationError: If creation fails
        """
        pass
    
    @abstractmethod
    async def get_refund_by_id(self, refund_id: UUID) -> Optional[Refund]:
        """Get refund by ID.
        
        Args:
            refund_id: Refund identifier
            
        Returns:
            Refund entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_refunds_by_transaction(self, transaction_id: UUID) -> List[Refund]:
        """Get all refunds for a transaction.
        
        Args:
            transaction_id: Transaction identifier
            
        Returns:
            List of refund entities
        """
        pass
    
    @abstractmethod
    async def get_refunds_by_restaurant(
        self,
        restaurant_id: UUID,
        limit: int = 50,
        offset: int = 0,
        status: Optional[RefundStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Refund]:
        """Get refunds for a restaurant with filtering and pagination.
        
        Args:
            restaurant_id: Restaurant identifier
            limit: Maximum number of refunds to return
            offset: Number of refunds to skip
            status: Filter by refund status
            start_date: Filter by start date
            end_date: Filter by end date
            
        Returns:
            List of refund entities
        """
        pass
    
    @abstractmethod
    async def update_refund(self, refund: Refund) -> Refund:
        """Update an existing refund.
        
        Args:
            refund: Refund entity with updates
            
        Returns:
            Updated refund entity
            
        Raises:
            RefundNotFoundError: If refund doesn't exist
            RefundUpdateError: If update fails
        """
        pass


class IPayoutRepository(ABC):
    """Repository interface for payout operations."""
    
    @abstractmethod
    async def create_payout(self, payout: Payout) -> Payout:
        """Create a new payout.
        
        Args:
            payout: Payout entity to create
            
        Returns:
            Created payout with generated ID and timestamps
            
        Raises:
            PayoutCreationError: If creation fails
        """
        pass
    
    @abstractmethod
    async def get_payout_by_id(self, payout_id: UUID) -> Optional[Payout]:
        """Get payout by ID.
        
        Args:
            payout_id: Payout identifier
            
        Returns:
            Payout entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_payouts_by_restaurant(
        self,
        restaurant_id: UUID,
        limit: int = 50,
        offset: int = 0,
        status: Optional[PayoutStatus] = None
    ) -> List[Payout]:
        """Get payouts for a restaurant with filtering and pagination.
        
        Args:
            restaurant_id: Restaurant identifier
            limit: Maximum number of payouts to return
            offset: Number of payouts to skip
            status: Filter by payout status
            
        Returns:
            List of payout entities
        """
        pass
    
    @abstractmethod
    async def update_payout(self, payout: Payout) -> Payout:
        """Update an existing payout.
        
        Args:
            payout: Payout entity with updates
            
        Returns:
            Updated payout entity
            
        Raises:
            PayoutNotFoundError: If payout doesn't exist
            PayoutUpdateError: If update fails
        """
        pass
    
    @abstractmethod
    async def get_scheduled_payouts(self, scheduled_date: date) -> List[Payout]:
        """Get payouts scheduled for a specific date.
        
        Args:
            scheduled_date: Date to check for scheduled payouts
            
        Returns:
            List of scheduled payout entities
        """
        pass


class IAuditLogRepository(ABC):
    """Repository interface for audit log operations."""
    
    @abstractmethod
    async def create_audit_log(
        self,
        entity_id: UUID,
        entity_type: str,
        action: str,
        previous_status: Optional[str] = None,
        new_status: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None,
        performed_by: Optional[UUID] = None
    ) -> UUID:
        """Create an audit log entry.
        
        Args:
            entity_id: ID of the entity being audited
            entity_type: Type of entity (transaction, refund, payout)
            action: Action performed
            previous_status: Previous status value
            new_status: New status value
            changes: Dictionary of changes made
            reason: Reason for the change
            performed_by: User who performed the action
            
        Returns:
            Audit log entry ID
        """
        pass
    
    @abstractmethod
    async def get_audit_logs_for_entity(
        self,
        entity_id: UUID,
        entity_type: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get audit logs for a specific entity.
        
        Args:
            entity_id: Entity identifier
            entity_type: Type of entity
            limit: Maximum number of logs to return
            offset: Number of logs to skip
            
        Returns:
            List of audit log entries
        """
        pass

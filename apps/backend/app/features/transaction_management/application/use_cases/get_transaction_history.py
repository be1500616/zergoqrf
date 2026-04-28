"""Get Transaction History Use Case.

This module implements the use case for retrieving transaction history
with filtering, pagination, and search capabilities.
"""

import logging
from datetime import date, datetime
from typing import Optional, List
from uuid import UUID

from ...domain.transaction_repos import ITransactionRepository
from ...domain.transaction_exceptions import TransactionError
from ..transaction_dtos import (
    TransactionHistoryRequestDTO,
    TransactionHistoryResponseDTO,
    TransactionDTO,
)

logger = logging.getLogger(__name__)


class GetTransactionHistoryUseCase:
    """Use case for retrieving transaction history.
    
    This use case provides comprehensive transaction history retrieval with
    filtering, pagination, and search capabilities for restaurant management.
    """
    
    def __init__(self, transaction_repository: ITransactionRepository):
        """Initialize the get transaction history use case.
        
        Args:
            transaction_repository: Repository for transaction operations
        """
        self._transaction_repo = transaction_repository
    
    async def execute(
        self,
        restaurant_id: UUID,
        request: TransactionHistoryRequestDTO
    ) -> TransactionHistoryResponseDTO:
        """Execute the get transaction history use case.
        
        Args:
            restaurant_id: Restaurant identifier
            request: Transaction history request parameters
            
        Returns:
            Transaction history response data
            
        Raises:
            TransactionError: If history retrieval fails
        """
        try:
            logger.info(
                "Retrieving transaction history for restaurant %s",
                restaurant_id,
                extra={
                    "restaurant_id": str(restaurant_id),
                    "limit": request.limit,
                    "offset": request.offset,
                    "status": request.status,
                    "payment_method": request.payment_method,
                    "start_date": request.start_date.isoformat() if request.start_date else None,
                    "end_date": request.end_date.isoformat() if request.end_date else None,
                    "search_term": request.search_term,
                }
            )
            
            # Validate request parameters
            self._validate_request(request)
            
            # Get transactions from repository
            transactions = await self._transaction_repo.get_transactions_by_restaurant(
                restaurant_id=restaurant_id,
                limit=request.limit,
                offset=request.offset,
                status=request.status,
                payment_method=request.payment_method,
                start_date=request.start_date,
                end_date=request.end_date,
                search_term=request.search_term
            )
            
            # Get total count for pagination
            total_count = await self._transaction_repo.count_transactions_by_restaurant(
                restaurant_id=restaurant_id,
                status=request.status,
                payment_method=request.payment_method,
                start_date=request.start_date,
                end_date=request.end_date,
                search_term=request.search_term
            )
            
            # Map transactions to DTOs
            transaction_dtos = [self._map_to_dto(transaction) for transaction in transactions]
            
            # Create response
            response = TransactionHistoryResponseDTO(
                transactions=transaction_dtos,
                total_count=total_count,
                has_more=request.offset + len(transaction_dtos) < total_count,
                page_info={
                    "current_page": (request.offset // request.limit) + 1,
                    "page_size": request.limit,
                    "total_pages": (total_count + request.limit - 1) // request.limit,
                }
            )
            
            logger.info(
                "Transaction history retrieved successfully",
                extra={
                    "restaurant_id": str(restaurant_id),
                    "transactions_count": len(transaction_dtos),
                    "total_count": total_count,
                    "has_more": response.has_more,
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(
                "Failed to retrieve transaction history",
                extra={
                    "restaurant_id": str(restaurant_id),
                    "error": str(e),
                },
                exc_info=True
            )
            raise TransactionError(f"Failed to retrieve transaction history: {str(e)}")
    
    async def get_transaction_by_number(
        self,
        restaurant_id: UUID,
        transaction_number: str
    ) -> Optional[TransactionDTO]:
        """Get a specific transaction by its number.
        
        Args:
            restaurant_id: Restaurant identifier
            transaction_number: Transaction number to search for
            
        Returns:
            Transaction DTO if found, None otherwise
            
        Raises:
            TransactionError: If retrieval fails
        """
        try:
            logger.info(
                "Retrieving transaction by number %s for restaurant %s",
                transaction_number,
                restaurant_id,
                extra={
                    "restaurant_id": str(restaurant_id),
                    "transaction_number": transaction_number,
                }
            )
            
            transaction = await self._transaction_repo.get_transaction_by_number(
                restaurant_id, transaction_number
            )
            
            if not transaction:
                logger.info(
                    "Transaction not found",
                    extra={
                        "restaurant_id": str(restaurant_id),
                        "transaction_number": transaction_number,
                    }
                )
                return None
            
            logger.info(
                "Transaction retrieved successfully",
                extra={
                    "restaurant_id": str(restaurant_id),
                    "transaction_id": str(transaction.id),
                    "transaction_number": transaction_number,
                }
            )
            
            return self._map_to_dto(transaction)
            
        except Exception as e:
            logger.error(
                "Failed to retrieve transaction by number",
                extra={
                    "restaurant_id": str(restaurant_id),
                    "transaction_number": transaction_number,
                    "error": str(e),
                },
                exc_info=True
            )
            raise TransactionError(f"Failed to retrieve transaction: {str(e)}")
    
    async def get_recent_transactions(
        self,
        restaurant_id: UUID,
        limit: int = 10
    ) -> List[TransactionDTO]:
        """Get recent transactions for a restaurant.
        
        Args:
            restaurant_id: Restaurant identifier
            limit: Maximum number of transactions to return
            
        Returns:
            List of recent transaction DTOs
            
        Raises:
            TransactionError: If retrieval fails
        """
        try:
            logger.info(
                "Retrieving recent transactions for restaurant %s",
                restaurant_id,
                extra={
                    "restaurant_id": str(restaurant_id),
                    "limit": limit,
                }
            )
            
            transactions = await self._transaction_repo.get_transactions_by_restaurant(
                restaurant_id=restaurant_id,
                limit=limit,
                offset=0,
                order_by="created_at",
                order_direction="DESC"
            )
            
            transaction_dtos = [self._map_to_dto(transaction) for transaction in transactions]
            
            logger.info(
                "Recent transactions retrieved successfully",
                extra={
                    "restaurant_id": str(restaurant_id),
                    "transactions_count": len(transaction_dtos),
                }
            )
            
            return transaction_dtos
            
        except Exception as e:
            logger.error(
                "Failed to retrieve recent transactions",
                extra={
                    "restaurant_id": str(restaurant_id),
                    "error": str(e),
                },
                exc_info=True
            )
            raise TransactionError(f"Failed to retrieve recent transactions: {str(e)}")
    
    def _validate_request(self, request: TransactionHistoryRequestDTO) -> None:
        """Validate transaction history request parameters.
        
        Args:
            request: Transaction history request
            
        Raises:
            ValueError: If request parameters are invalid
        """
        if request.limit <= 0 or request.limit > 100:
            raise ValueError("Limit must be between 1 and 100")
        
        if request.offset < 0:
            raise ValueError("Offset must be non-negative")
        
        if request.start_date and request.end_date:
            if request.start_date > request.end_date:
                raise ValueError("Start date must be before or equal to end date")
        
        if request.end_date and request.end_date > date.today():
            raise ValueError("End date cannot be in the future")
        
        # Validate search term length
        if request.search_term and len(request.search_term.strip()) < 2:
            raise ValueError("Search term must be at least 2 characters long")
    
    def _map_to_dto(self, transaction) -> TransactionDTO:
        """Map transaction entity to DTO.
        
        Args:
            transaction: Transaction entity
            
        Returns:
            Transaction DTO
        """
        from ..transaction_dtos import MoneyDTO
        
        return TransactionDTO(
            id=transaction.id,
            transaction_number=transaction.transaction_number.value,
            restaurant_id=transaction.restaurant_id,
            order_id=transaction.order_id,
            amount=MoneyDTO(
                amount=transaction.amount.amount,
                currency=transaction.amount.currency
            ),
            payment_method=transaction.payment_method,
            status=transaction.status,
            customer_name=transaction.customer_name,
            customer_phone=transaction.customer_phone,
            customer_email=transaction.customer_email,
            description=transaction.description,
            reference_number=transaction.reference_number,
            gateway_transaction_id=transaction.gateway_transaction_id,
            gateway_order_id=transaction.gateway_order_id,
            failure_reason=transaction.failure_reason,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at,
            processed_at=transaction.processed_at
        )

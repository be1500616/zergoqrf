"""Payment Gateway Integration Interfaces.

This module defines the interfaces for payment gateway integration
following the Adapter pattern for loose coupling with external services.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import UUID

from .transaction_vos import Money, PaymentMethod, TransactionStatus, RefundStatus


class PaymentRequest:
    """Payment request data structure."""
    
    def __init__(
        self,
        amount: Money,
        payment_method: PaymentMethod,
        customer_name: Optional[str] = None,
        customer_email: Optional[str] = None,
        customer_phone: Optional[str] = None,
        description: Optional[str] = None,
        order_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize payment request.
        
        Args:
            amount: Payment amount
            payment_method: Payment method
            customer_name: Customer name
            customer_email: Customer email
            customer_phone: Customer phone
            description: Payment description
            order_id: Associated order ID
            metadata: Additional metadata
        """
        self.amount = amount
        self.payment_method = payment_method
        self.customer_name = customer_name
        self.customer_email = customer_email
        self.customer_phone = customer_phone
        self.description = description
        self.order_id = order_id
        self.metadata = metadata or {}


class PaymentResponse:
    """Payment response data structure."""
    
    def __init__(
        self,
        success: bool,
        gateway_transaction_id: Optional[str] = None,
        gateway_order_id: Optional[str] = None,
        status: Optional[TransactionStatus] = None,
        gateway_response: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        error_code: Optional[str] = None
    ):
        """Initialize payment response.
        
        Args:
            success: Whether payment was successful
            gateway_transaction_id: Gateway transaction ID
            gateway_order_id: Gateway order ID
            status: Payment status
            gateway_response: Full gateway response
            error_message: Error message if failed
            error_code: Error code if failed
        """
        self.success = success
        self.gateway_transaction_id = gateway_transaction_id
        self.gateway_order_id = gateway_order_id
        self.status = status
        self.gateway_response = gateway_response or {}
        self.error_message = error_message
        self.error_code = error_code


class RefundRequest:
    """Refund request data structure."""
    
    def __init__(
        self,
        gateway_transaction_id: str,
        amount: Money,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize refund request.
        
        Args:
            gateway_transaction_id: Original transaction ID from gateway
            amount: Refund amount
            reason: Reason for refund
            metadata: Additional metadata
        """
        self.gateway_transaction_id = gateway_transaction_id
        self.amount = amount
        self.reason = reason
        self.metadata = metadata or {}


class RefundResponse:
    """Refund response data structure."""
    
    def __init__(
        self,
        success: bool,
        gateway_refund_id: Optional[str] = None,
        status: Optional[RefundStatus] = None,
        gateway_response: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        error_code: Optional[str] = None
    ):
        """Initialize refund response.
        
        Args:
            success: Whether refund was successful
            gateway_refund_id: Gateway refund ID
            status: Refund status
            gateway_response: Full gateway response
            error_message: Error message if failed
            error_code: Error code if failed
        """
        self.success = success
        self.gateway_refund_id = gateway_refund_id
        self.status = status
        self.gateway_response = gateway_response or {}
        self.error_message = error_message
        self.error_code = error_code


class WebhookEvent:
    """Webhook event data structure."""
    
    def __init__(
        self,
        event_type: str,
        gateway_transaction_id: Optional[str] = None,
        gateway_refund_id: Optional[str] = None,
        status: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        signature: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        """Initialize webhook event.
        
        Args:
            event_type: Type of webhook event
            gateway_transaction_id: Gateway transaction ID
            gateway_refund_id: Gateway refund ID
            status: New status from webhook
            payload: Full webhook payload
            signature: Webhook signature for verification
            timestamp: Event timestamp
        """
        self.event_type = event_type
        self.gateway_transaction_id = gateway_transaction_id
        self.gateway_refund_id = gateway_refund_id
        self.status = status
        self.payload = payload or {}
        self.signature = signature
        self.timestamp = timestamp or datetime.utcnow()


class IPaymentGateway(ABC):
    """Interface for payment gateway operations.
    
    This interface defines the contract for payment gateway integrations
    allowing for multiple payment providers to be supported.
    """
    
    @property
    @abstractmethod
    def gateway_name(self) -> str:
        """Get the name of the payment gateway.
        
        Returns:
            Gateway name (e.g., 'stripe', 'razorpay', 'paypal')
        """
        pass
    
    @property
    @abstractmethod
    def supported_payment_methods(self) -> List[PaymentMethod]:
        """Get supported payment methods for this gateway.
        
        Returns:
            List of supported payment methods
        """
        pass
    
    @abstractmethod
    async def create_payment_intent(self, request: PaymentRequest) -> PaymentResponse:
        """Create a payment intent with the gateway.
        
        Args:
            request: Payment request details
            
        Returns:
            Payment response with gateway details
            
        Raises:
            PaymentGatewayError: If payment creation fails
        """
        pass
    
    @abstractmethod
    async def capture_payment(
        self, 
        gateway_transaction_id: str,
        amount: Optional[Money] = None
    ) -> PaymentResponse:
        """Capture a previously authorized payment.
        
        Args:
            gateway_transaction_id: Gateway transaction ID
            amount: Amount to capture (optional, defaults to full amount)
            
        Returns:
            Payment response with capture details
            
        Raises:
            PaymentGatewayError: If capture fails
        """
        pass
    
    @abstractmethod
    async def get_payment_status(self, gateway_transaction_id: str) -> PaymentResponse:
        """Get the current status of a payment.
        
        Args:
            gateway_transaction_id: Gateway transaction ID
            
        Returns:
            Payment response with current status
            
        Raises:
            PaymentGatewayError: If status check fails
        """
        pass
    
    @abstractmethod
    async def process_refund(self, request: RefundRequest) -> RefundResponse:
        """Process a refund for a payment.
        
        Args:
            request: Refund request details
            
        Returns:
            Refund response with gateway details
            
        Raises:
            PaymentGatewayError: If refund fails
        """
        pass
    
    @abstractmethod
    async def get_refund_status(self, gateway_refund_id: str) -> RefundResponse:
        """Get the current status of a refund.
        
        Args:
            gateway_refund_id: Gateway refund ID
            
        Returns:
            Refund response with current status
            
        Raises:
            PaymentGatewayError: If status check fails
        """
        pass
    
    @abstractmethod
    async def verify_webhook_signature(
        self, 
        payload: bytes, 
        signature: str,
        webhook_secret: str
    ) -> bool:
        """Verify webhook signature for security.
        
        Args:
            payload: Raw webhook payload
            signature: Webhook signature
            webhook_secret: Webhook secret key
            
        Returns:
            True if signature is valid
        """
        pass
    
    @abstractmethod
    async def parse_webhook_event(self, payload: Dict[str, Any]) -> WebhookEvent:
        """Parse webhook payload into standardized event.
        
        Args:
            payload: Webhook payload
            
        Returns:
            Standardized webhook event
            
        Raises:
            PaymentGatewayError: If parsing fails
        """
        pass


class IPayoutGateway(ABC):
    """Interface for payout operations.
    
    This interface defines the contract for restaurant payout operations
    through payment gateways that support marketplace/connect functionality.
    """
    
    @abstractmethod
    async def create_payout(
        self,
        restaurant_id: UUID,
        amount: Money,
        bank_account_id: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a payout to restaurant's bank account.
        
        Args:
            restaurant_id: Restaurant identifier
            amount: Payout amount
            bank_account_id: Bank account identifier
            description: Payout description
            metadata: Additional metadata
            
        Returns:
            Payout response with gateway details
            
        Raises:
            PaymentGatewayError: If payout creation fails
        """
        pass
    
    @abstractmethod
    async def get_payout_status(self, gateway_payout_id: str) -> Dict[str, Any]:
        """Get the current status of a payout.
        
        Args:
            gateway_payout_id: Gateway payout ID
            
        Returns:
            Payout status information
            
        Raises:
            PaymentGatewayError: If status check fails
        """
        pass
    
    @abstractmethod
    async def get_account_balance(self, restaurant_id: UUID) -> Dict[str, Any]:
        """Get account balance for a restaurant.
        
        Args:
            restaurant_id: Restaurant identifier
            
        Returns:
            Account balance information
            
        Raises:
            PaymentGatewayError: If balance check fails
        """
        pass


class PaymentGatewayError(Exception):
    """Base exception for payment gateway errors."""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        gateway_response: Optional[Dict[str, Any]] = None
    ):
        """Initialize payment gateway error.
        
        Args:
            message: Error message
            error_code: Gateway-specific error code
            gateway_response: Full gateway response
        """
        super().__init__(message)
        self.error_code = error_code
        self.gateway_response = gateway_response or {}


class PaymentGatewayFactory:
    """Factory for creating payment gateway instances.
    
    This factory allows for dynamic selection of payment gateways
    based on configuration or business rules.
    """
    
    def __init__(self):
        """Initialize payment gateway factory."""
        self._gateways: Dict[str, IPaymentGateway] = {}
        self._payout_gateways: Dict[str, IPayoutGateway] = {}
    
    def register_payment_gateway(self, name: str, gateway: IPaymentGateway) -> None:
        """Register a payment gateway.
        
        Args:
            name: Gateway name
            gateway: Gateway implementation
        """
        self._gateways[name] = gateway
    
    def register_payout_gateway(self, name: str, gateway: IPayoutGateway) -> None:
        """Register a payout gateway.
        
        Args:
            name: Gateway name
            gateway: Gateway implementation
        """
        self._payout_gateways[name] = gateway
    
    def get_payment_gateway(self, name: str) -> IPaymentGateway:
        """Get payment gateway by name.
        
        Args:
            name: Gateway name
            
        Returns:
            Payment gateway instance
            
        Raises:
            ValueError: If gateway not found
        """
        if name not in self._gateways:
            raise ValueError(f"Payment gateway '{name}' not registered")
        
        return self._gateways[name]
    
    def get_payout_gateway(self, name: str) -> IPayoutGateway:
        """Get payout gateway by name.
        
        Args:
            name: Gateway name
            
        Returns:
            Payout gateway instance
            
        Raises:
            ValueError: If gateway not found
        """
        if name not in self._payout_gateways:
            raise ValueError(f"Payout gateway '{name}' not registered")
        
        return self._payout_gateways[name]
    
    def get_available_payment_gateways(self) -> List[str]:
        """Get list of available payment gateways.
        
        Returns:
            List of gateway names
        """
        return list(self._gateways.keys())
    
    def get_available_payout_gateways(self) -> List[str]:
        """Get list of available payout gateways.
        
        Returns:
            List of gateway names
        """
        return list(self._payout_gateways.keys())

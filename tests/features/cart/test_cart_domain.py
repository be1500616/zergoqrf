"""Unit tests for cart domain entities and value objects.

This module contains unit tests for the core domain logic of the cart system,
including entities, value objects, and domain services.
"""

import pytest
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from apps.backend.app.features.cart.domain.cart_entities import CartSession, CartItem, SessionType
from apps.backend.app.features.cart.domain.cart_vos import (
    Money, Quantity, CartSessionToken, CustomizationOptions
)
from apps.backend.app.features.cart.domain.cart_exceptions import (
    InvalidQuantityError, CartFullError
)


class TestMoney:
    """Test cases for Money value object."""
    
    def test_money_creation_valid(self):
        """Test creating money with valid amount."""
        money = Money(Decimal("10.50"))
        assert money.amount == Decimal("10.50")
    
    def test_money_creation_negative_raises_error(self):
        """Test creating money with negative amount raises error."""
        with pytest.raises(ValueError, match="Money amount cannot be negative"):
            Money(Decimal("-5.00"))
    
    def test_money_equality(self):
        """Test money equality comparison."""
        money1 = Money(Decimal("10.50"))
        money2 = Money(Decimal("10.50"))
        money3 = Money(Decimal("15.00"))
        
        assert money1 == money2
        assert money1 != money3
    
    def test_money_addition(self):
        """Test money addition."""
        money1 = Money(Decimal("10.50"))
        money2 = Money(Decimal("5.25"))
        result = money1.add(money2)
        
        assert result.amount == Decimal("15.75")
    
    def test_money_subtraction(self):
        """Test money subtraction."""
        money1 = Money(Decimal("10.50"))
        money2 = Money(Decimal("5.25"))
        result = money1.subtract(money2)
        
        assert result.amount == Decimal("5.25")
    
    def test_money_subtraction_negative_raises_error(self):
        """Test money subtraction resulting in negative raises error."""
        money1 = Money(Decimal("5.00"))
        money2 = Money(Decimal("10.00"))
        
        with pytest.raises(ValueError, match="Cannot subtract to negative amount"):
            money1.subtract(money2)
    
    def test_money_multiplication(self):
        """Test money multiplication."""
        money = Money(Decimal("10.50"))
        result = money.multiply(Decimal("2"))
        
        assert result.amount == Decimal("21.00")


class TestQuantity:
    """Test cases for Quantity value object."""
    
    def test_quantity_creation_valid(self):
        """Test creating quantity with valid value."""
        quantity = Quantity(5)
        assert quantity.value == 5
    
    def test_quantity_creation_zero_raises_error(self):
        """Test creating quantity with zero raises error."""
        with pytest.raises(ValueError, match="Quantity must be positive"):
            Quantity(0)
    
    def test_quantity_creation_negative_raises_error(self):
        """Test creating quantity with negative value raises error."""
        with pytest.raises(ValueError, match="Quantity must be positive"):
            Quantity(-1)
    
    def test_quantity_equality(self):
        """Test quantity equality comparison."""
        quantity1 = Quantity(5)
        quantity2 = Quantity(5)
        quantity3 = Quantity(10)
        
        assert quantity1 == quantity2
        assert quantity1 != quantity3
    
    def test_quantity_addition(self):
        """Test quantity addition."""
        quantity1 = Quantity(5)
        quantity2 = Quantity(3)
        result = quantity1.add(quantity2)
        
        assert result.value == 8
    
    def test_quantity_subtraction(self):
        """Test quantity subtraction."""
        quantity1 = Quantity(10)
        quantity2 = Quantity(3)
        result = quantity1.subtract(quantity2)
        
        assert result.value == 7
    
    def test_quantity_subtraction_to_zero_raises_error(self):
        """Test quantity subtraction to zero raises error."""
        quantity1 = Quantity(5)
        quantity2 = Quantity(5)
        
        with pytest.raises(ValueError, match="Cannot subtract to zero or negative quantity"):
            quantity1.subtract(quantity2)


class TestCartSessionToken:
    """Test cases for CartSessionToken value object."""
    
    def test_token_creation_valid(self):
        """Test creating token with valid value."""
        token = CartSessionToken("abcdef1234567890")
        assert token.value == "abcdef1234567890"
    
    def test_token_creation_empty_raises_error(self):
        """Test creating token with empty value raises error."""
        with pytest.raises(ValueError, match="Session token must be a non-empty string"):
            CartSessionToken("")
    
    def test_token_creation_short_raises_error(self):
        """Test creating token with short value raises error."""
        with pytest.raises(ValueError, match="Session token must be at least 16 characters"):
            CartSessionToken("short")
    
    def test_token_equality(self):
        """Test token equality comparison."""
        token1 = CartSessionToken("abcdef1234567890")
        token2 = CartSessionToken("abcdef1234567890")
        token3 = CartSessionToken("different1234567890")
        
        assert token1 == token2
        assert token1 != token3


class TestCustomizationOptions:
    """Test cases for CustomizationOptions value object."""
    
    def test_customizations_creation_empty(self):
        """Test creating empty customizations."""
        customizations = CustomizationOptions({})
        assert customizations.is_empty()
        assert customizations.options == {}
    
    def test_customizations_creation_with_options(self):
        """Test creating customizations with options."""
        options = {"size": "large", "extra_cheese": True}
        customizations = CustomizationOptions(options)
        
        assert not customizations.is_empty()
        assert customizations.get("size") == "large"
        assert customizations.get("extra_cheese") is True
        assert customizations.has_option("size")
        assert not customizations.has_option("nonexistent")
    
    def test_customizations_equality(self):
        """Test customizations equality comparison."""
        options1 = {"size": "large", "extra_cheese": True}
        options2 = {"size": "large", "extra_cheese": True}
        options3 = {"size": "medium"}
        
        customizations1 = CustomizationOptions(options1)
        customizations2 = CustomizationOptions(options2)
        customizations3 = CustomizationOptions(options3)
        
        assert customizations1 == customizations2
        assert customizations1 != customizations3


class TestCartSession:
    """Test cases for CartSession entity."""
    
    def test_cart_session_creation_anonymous(self):
        """Test creating anonymous cart session."""
        session_id = uuid4()
        token = CartSessionToken("abcdef1234567890")
        restaurant_id = uuid4()
        anonymous_session_id = uuid4()
        expires_at = datetime.now(timezone.utc)
        
        session = CartSession(
            id=session_id,
            session_token=token,
            session_type=SessionType.ANONYMOUS,
            restaurant_id=restaurant_id,
            anonymous_session_id=anonymous_session_id,
            expires_at=expires_at,
        )
        
        assert session.id == session_id
        assert session.session_token == token
        assert session.session_type == SessionType.ANONYMOUS
        assert session.restaurant_id == restaurant_id
        assert session.anonymous_session_id == anonymous_session_id
        assert session.user_id is None
        assert session.is_active
    
    def test_cart_session_creation_authenticated(self):
        """Test creating authenticated cart session."""
        session_id = uuid4()
        token = CartSessionToken("abcdef1234567890")
        restaurant_id = uuid4()
        user_id = uuid4()
        expires_at = datetime.now(timezone.utc)
        
        session = CartSession(
            id=session_id,
            session_token=token,
            session_type=SessionType.AUTHENTICATED,
            restaurant_id=restaurant_id,
            user_id=user_id,
            expires_at=expires_at,
        )
        
        assert session.id == session_id
        assert session.session_token == token
        assert session.session_type == SessionType.AUTHENTICATED
        assert session.restaurant_id == restaurant_id
        assert session.user_id == user_id
        assert session.anonymous_session_id is None
        assert session.is_active
    
    def test_cart_session_invalid_anonymous_constraints(self):
        """Test cart session with invalid anonymous constraints raises error."""
        with pytest.raises(ValueError, match="Anonymous sessions must have anonymous_session_id"):
            CartSession(
                id=uuid4(),
                session_token=CartSessionToken("abcdef1234567890"),
                session_type=SessionType.ANONYMOUS,
                restaurant_id=uuid4(),
                user_id=uuid4(),  # Invalid: anonymous session with user_id
                expires_at=datetime.now(timezone.utc),
            )
    
    def test_cart_session_invalid_authenticated_constraints(self):
        """Test cart session with invalid authenticated constraints raises error."""
        with pytest.raises(ValueError, match="Authenticated sessions must have user_id"):
            CartSession(
                id=uuid4(),
                session_token=CartSessionToken("abcdef1234567890"),
                session_type=SessionType.AUTHENTICATED,
                restaurant_id=uuid4(),
                anonymous_session_id=uuid4(),  # Invalid: authenticated session with anonymous_session_id
                expires_at=datetime.now(timezone.utc),
            )
    
    def test_cart_session_is_expired(self):
        """Test cart session expiration check."""
        past_time = datetime(2020, 1, 1, tzinfo=timezone.utc)
        future_time = datetime(2030, 1, 1, tzinfo=timezone.utc)
        
        expired_session = CartSession(
            id=uuid4(),
            session_token=CartSessionToken("abcdef1234567890"),
            session_type=SessionType.ANONYMOUS,
            restaurant_id=uuid4(),
            anonymous_session_id=uuid4(),
            expires_at=past_time,
        )
        
        valid_session = CartSession(
            id=uuid4(),
            session_token=CartSessionToken("abcdef1234567890"),
            session_type=SessionType.ANONYMOUS,
            restaurant_id=uuid4(),
            anonymous_session_id=uuid4(),
            expires_at=future_time,
        )
        
        assert expired_session.is_expired()
        assert not valid_session.is_expired()
    
    def test_cart_session_update_totals(self):
        """Test updating cart session totals."""
        session = CartSession(
            id=uuid4(),
            session_token=CartSessionToken("abcdef1234567890"),
            session_type=SessionType.ANONYMOUS,
            restaurant_id=uuid4(),
            anonymous_session_id=uuid4(),
            expires_at=datetime.now(timezone.utc),
        )
        
        session.update_totals(5, Money(Decimal("25.50")))
        
        assert session.item_count == 5
        assert session.total_amount.amount == Decimal("25.50")
    
    def test_cart_session_update_totals_exceeds_limit(self):
        """Test updating cart session totals exceeding limit raises error."""
        session = CartSession(
            id=uuid4(),
            session_token=CartSessionToken("abcdef1234567890"),
            session_type=SessionType.ANONYMOUS,
            restaurant_id=uuid4(),
            anonymous_session_id=uuid4(),
            expires_at=datetime.now(timezone.utc),
        )
        
        with pytest.raises(ValueError, match="Cart cannot exceed 50 items"):
            session.update_totals(51, Money(Decimal("100.00")))

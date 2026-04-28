"""Clean Architecture authentication router.

This module provides HTTP endpoints for authentication operations,
delegating business logic to use cases in the application layer.
"""

from fastapi import APIRouter, Depends, HTTPException

from ..application.auth_dtos import (
    AnonymousSessionRequestDTO,
    SignInRequestDTO,
    SignUpRequestDTO,
    TokenRefreshRequestDTO,
)
from ..application.dependencies import (
    get_anonymous_session_use_case,
    get_current_user_use_case,
    get_refresh_token_use_case,
    get_signin_use_case,
    get_signup_use_case,
)
from ..application.use_cases import (
    AnonymousSessionUseCase,
    GetCurrentUserUseCase,
    RefreshTokenUseCase,
    SignInUseCase,
    SignUpUseCase,
)
from ..domain.auth_exceptions import AuthenticationError
from .auth_exception_handlers import map_auth_exception_to_http
from .auth_schemas import (
    AnonymousSessionResponse,
    AnonymousSessionSchema,
    RefreshTokenSchema,
    SignInSchema,
    SignUpSchema,
    TokenSchema,
    UserProfileResponse,
)

router = APIRouter()


@router.post("/signup", response_model=TokenSchema)
async def signup(
    user_data: SignUpSchema,
    signup_use_case: SignUpUseCase = Depends(get_signup_use_case),
):
    """Register a new user with email and password.

    Args:
        user_data: User registration data
        signup_use_case: Sign up use case dependency

    Returns:
        Authentication token response

    Raises:
        HTTPException: If registration fails
    """
    try:
        # Convert Pydantic schema to DTO
        signup_request = SignUpRequestDTO(
            email=user_data.email,
            password=user_data.password,
            name=user_data.name,
            phone=user_data.phone,
            role=user_data.role,
            restaurant_id=user_data.restaurant_id,
        )

        # Execute use case
        auth_response = await signup_use_case.execute(signup_request)

        # Convert DTO to Pydantic response schema
        from .auth_schemas import UserInfo

        user_info = UserInfo(
            id=auth_response.user.id,
            email=auth_response.user.email,
            role=auth_response.user.role,
            restaurant_id=auth_response.user.restaurant_id,
        )

        return TokenSchema(
            access_token=auth_response.access_token,
            refresh_token=auth_response.refresh_token,
            token_type=auth_response.token_type,
            expires_in=auth_response.expires_in,
            user=user_info,
        )

    except AuthenticationError as e:
        # Map domain exceptions to HTTP exceptions
        http_exception = map_auth_exception_to_http(e)
        raise http_exception
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/signin", response_model=TokenSchema)
async def signin(
    user_data: SignInSchema,
    signin_use_case: SignInUseCase = Depends(get_signin_use_case),
):
    """Sign in with email and password.

    Args:
        user_data: User sign in credentials
        signin_use_case: Sign in use case dependency

    Returns:
        Authentication token response

    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Convert Pydantic schema to DTO
        signin_request = SignInRequestDTO(
            email=user_data.email,
            password=user_data.password,
        )

        # Execute use case
        auth_response = await signin_use_case.execute(signin_request)

        # Convert DTO to Pydantic response schema
        from .auth_schemas import UserInfo

        user_info = UserInfo(
            id=auth_response.user.id,
            email=auth_response.user.email,
            role=auth_response.user.role,
            restaurant_id=auth_response.user.restaurant_id,
        )

        return TokenSchema(
            access_token=auth_response.access_token,
            refresh_token=auth_response.refresh_token,
            token_type=auth_response.token_type,
            expires_in=auth_response.expires_in,
            user=user_info,
        )

    except AuthenticationError as e:
        # Map domain exceptions to HTTP exceptions
        http_exception = map_auth_exception_to_http(e)
        raise http_exception
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/anonymous-session", response_model=AnonymousSessionResponse)
async def create_anonymous_session(
    session_data: AnonymousSessionSchema,
    anonymous_session_use_case: AnonymousSessionUseCase = Depends(
        get_anonymous_session_use_case
    ),
):
    """Create an anonymous session for QR code users.

    Args:
        session_data: Anonymous session request data
        anonymous_session_use_case: Anonymous session use case dependency

    Returns:
        Anonymous session response

    Raises:
        HTTPException: If session creation fails
    """
    try:
        # Convert Pydantic schema to DTO
        session_request = AnonymousSessionRequestDTO(
            restaurant_id=str(session_data.restaurant_id),
            table_id=str(session_data.table_id),
        )

        # Execute use case
        session_response = await anonymous_session_use_case.execute(session_request)

        # Convert DTO to Pydantic response schema
        return AnonymousSessionResponse(
            session_id=session_response.session_id,
            session_token=session_response.session_token,
            expires_at=session_response.expires_at,
            restaurant_id=session_response.restaurant_id,
            table_id=session_response.table_id,
        )

    except AuthenticationError as e:
        # Map domain exceptions to HTTP exceptions
        http_exception = map_auth_exception_to_http(e)
        raise http_exception
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/refresh", response_model=TokenSchema)
async def refresh_token(
    token_data: RefreshTokenSchema,
    refresh_token_use_case: RefreshTokenUseCase = Depends(get_refresh_token_use_case),
):
    """Refresh an access token using a refresh token.

    Args:
        token_data: Refresh token request data
        refresh_token_use_case: Refresh token use case dependency

    Returns:
        New authentication token response

    Raises:
        HTTPException: If token refresh fails
    """
    try:
        # Convert Pydantic schema to DTO
        refresh_request = TokenRefreshRequestDTO(
            refresh_token=token_data.refresh_token,
        )

        # Execute use case
        auth_response = await refresh_token_use_case.execute(refresh_request)

        # Convert DTO to Pydantic response schema
        from .auth_schemas import UserInfo

        user_info = UserInfo(
            id=auth_response.user.id,
            email=auth_response.user.email,
            role=auth_response.user.role,
            restaurant_id=auth_response.user.restaurant_id,
        )

        return TokenSchema(
            access_token=auth_response.access_token,
            refresh_token=auth_response.refresh_token,
            token_type=auth_response.token_type,
            expires_in=auth_response.expires_in,
            user=user_info,
        )

    except AuthenticationError as e:
        # Map domain exceptions to HTTP exceptions
        http_exception = map_auth_exception_to_http(e)
        raise http_exception
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user(
    current_user_use_case: GetCurrentUserUseCase = Depends(get_current_user_use_case),
):
    """Get current user profile.

    Args:
        current_user_use_case: Get current user use case dependency

    Returns:
        Current user profile

    Raises:
        HTTPException: If user retrieval fails
    """
    try:
        # This would need to extract the token from the Authorization header
        # For now, this is a placeholder implementation
        # TODO: Implement proper token extraction and validation

        # user_dto = await current_user_use_case.execute(access_token)
        # return UserProfileResponse(...)

        raise HTTPException(
            status_code=501, detail="Get current user endpoint not yet implemented"
        )

    except AuthenticationError as e:
        # Map domain exceptions to HTTP exceptions
        http_exception = map_auth_exception_to_http(e)
        raise http_exception
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

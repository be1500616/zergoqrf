"""Dependency injection configuration for authentication feature.

This module provides dependency injection setup for the authentication
system, following Clean Architecture principles.
"""

from fastapi import Depends
from supabase import Client

from app.common.supabase_client import get_supabase
from ..domain.auth_repos import IUserRepository, IAuthSessionRepository
from ..infrastructure.auth_repos_impl import UserRepositoryImpl, AuthSessionRepositoryImpl
from .use_cases import (
    SignUpUseCase,
    SignInUseCase,
    RefreshTokenUseCase,
    AnonymousSessionUseCase,
    GetCurrentUserUseCase,
)


# Repository Dependencies
def get_user_repository(
    supabase_client: Client = Depends(get_supabase),
) -> IUserRepository:
    """Get user repository implementation.
    
    Args:
        supabase_client: Supabase client dependency
        
    Returns:
        User repository implementation
    """
    return UserRepositoryImpl(supabase_client)


def get_session_repository(
    supabase_client: Client = Depends(get_supabase),
) -> IAuthSessionRepository:
    """Get session repository implementation.
    
    Args:
        supabase_client: Supabase client dependency
        
    Returns:
        Session repository implementation
    """
    return AuthSessionRepositoryImpl(supabase_client)


# Use Case Dependencies
def get_signup_use_case(
    user_repository: IUserRepository = Depends(get_user_repository),
    session_repository: IAuthSessionRepository = Depends(get_session_repository),
) -> SignUpUseCase:
    """Get sign up use case.
    
    Args:
        user_repository: User repository dependency
        session_repository: Session repository dependency
        
    Returns:
        Sign up use case instance
    """
    return SignUpUseCase(user_repository, session_repository)


def get_signin_use_case(
    user_repository: IUserRepository = Depends(get_user_repository),
    session_repository: IAuthSessionRepository = Depends(get_session_repository),
) -> SignInUseCase:
    """Get sign in use case.
    
    Args:
        user_repository: User repository dependency
        session_repository: Session repository dependency
        
    Returns:
        Sign in use case instance
    """
    return SignInUseCase(user_repository, session_repository)


def get_refresh_token_use_case(
    user_repository: IUserRepository = Depends(get_user_repository),
    session_repository: IAuthSessionRepository = Depends(get_session_repository),
) -> RefreshTokenUseCase:
    """Get refresh token use case.
    
    Args:
        user_repository: User repository dependency
        session_repository: Session repository dependency
        
    Returns:
        Refresh token use case instance
    """
    return RefreshTokenUseCase(user_repository, session_repository)


def get_anonymous_session_use_case(
    session_repository: IAuthSessionRepository = Depends(get_session_repository),
) -> AnonymousSessionUseCase:
    """Get anonymous session use case.
    
    Args:
        session_repository: Session repository dependency
        
    Returns:
        Anonymous session use case instance
    """
    return AnonymousSessionUseCase(session_repository)


def get_current_user_use_case(
    user_repository: IUserRepository = Depends(get_user_repository),
    session_repository: IAuthSessionRepository = Depends(get_session_repository),
) -> GetCurrentUserUseCase:
    """Get current user use case.
    
    Args:
        user_repository: User repository dependency
        session_repository: Session repository dependency
        
    Returns:
        Get current user use case instance
    """
    return GetCurrentUserUseCase(user_repository, session_repository)

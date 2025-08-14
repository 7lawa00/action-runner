from flask import session, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from typing import Dict, Any, Optional
from ..models import User
from .. import db

class AuthService:
    """Service to handle authentication and authorization"""
    
    @staticmethod
    def register_user(username: str, email: str, password: str, role: str = 'user') -> Dict[str, Any]:
        """Register a new user"""
        try:
            # Check if user already exists
            if User.query.filter_by(username=username).first():
                return {'success': False, 'error': 'Username already exists'}
            
            if User.query.filter_by(email=email).first():
                return {'success': False, 'error': 'Email already exists'}
            
            # Create new user
            user = User(username=username, email=email, role=role)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'User registered successfully',
                'user_id': user.id
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Dict[str, Any]:
        """Authenticate user login"""
        try:
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password) and user.is_active:
                login_user(user)
                return {
                    'success': True,
                    'message': 'Login successful',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'role': user.role
                    }
                }
            else:
                return {'success': False, 'error': 'Invalid credentials'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def logout_user_session() -> Dict[str, Any]:
        """Logout current user"""
        try:
            logout_user()
            return {'success': True, 'message': 'Logout successful'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_current_user() -> Optional[User]:
        """Get current authenticated user"""
        if current_user.is_authenticated:
            return current_user
        return None
    
    @staticmethod
    def require_role(required_role: str):
        """Decorator to require specific user role"""
        def decorator(f):
            @wraps(f)
            @login_required
            def decorated_function(*args, **kwargs):
                if not current_user.is_authenticated:
                    return jsonify({'error': 'Authentication required'}), 401
                
                if current_user.role != required_role and current_user.role != 'admin':
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @staticmethod
    def require_permission(resource_type: str, resource_id: int, permission: str = 'read'):
        """Decorator to check resource-specific permissions"""
        def decorator(f):
            @wraps(f)
            @login_required
            def decorated_function(*args, **kwargs):
                if not current_user.is_authenticated:
                    return jsonify({'error': 'Authentication required'}), 401
                
                # Admin has all permissions
                if current_user.role == 'admin':
                    return f(*args, **kwargs)
                
                # Check resource ownership or sharing
                if AuthService.has_permission(resource_type, resource_id, permission):
                    return f(*args, **kwargs)
                else:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
            return decorated_function
        return decorator
    
    @staticmethod
    def has_permission(resource_type: str, resource_id: int, permission: str = 'read') -> bool:
        """Check if current user has permission for a resource"""
        if not current_user.is_authenticated:
            return False
        
        # Admin has all permissions
        if current_user.role == 'admin':
            return True
        
        try:
            if resource_type == 'test_case':
                from ..models import TestCase, TestCaseShare
                
                # Check ownership
                test_case = TestCase.query.filter_by(id=resource_id, created_by_id=current_user.id).first()
                if test_case:
                    return True
                
                # Check if public
                test_case = TestCase.query.filter_by(id=resource_id, is_public=True).first()
                if test_case and permission == 'read':
                    return True
                
                # Check sharing
                share = TestCaseShare.query.filter_by(
                    test_case_id=resource_id,
                    shared_with_id=current_user.id
                ).first()
                
                if share:
                    if permission == 'read':
                        return True
                    elif permission == 'write' and share.permission in ['write', 'execute']:
                        return True
                    elif permission == 'execute' and share.permission == 'execute':
                        return True
            
            elif resource_type == 'test_suite':
                from ..models import TestSuite, TestSuiteShare
                
                # Check ownership
                test_suite = TestSuite.query.filter_by(id=resource_id, created_by_id=current_user.id).first()
                if test_suite:
                    return True
                
                # Check if public
                test_suite = TestSuite.query.filter_by(id=resource_id, is_public=True).first()
                if test_suite and permission == 'read':
                    return True
                
                # Check sharing
                share = TestSuiteShare.query.filter_by(
                    test_suite_id=resource_id,
                    shared_with_id=current_user.id
                ).first()
                
                if share:
                    if permission == 'read':
                        return True
                    elif permission == 'write' and share.permission in ['write', 'execute']:
                        return True
                    elif permission == 'execute' and share.permission == 'execute':
                        return True
            
            return False
            
        except Exception:
            return False

def require_auth(f):
    """Simple authentication decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def require_admin(f):
    """Admin role decorator"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function
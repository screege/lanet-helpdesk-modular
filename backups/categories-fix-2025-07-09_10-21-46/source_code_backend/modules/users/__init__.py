#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Users Module
Complete user management functionality with CRUD operations
"""

from .routes import users_bp
from .service import UserService

__all__ = ['users_bp', 'UserService']
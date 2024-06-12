"""
This module provides utility functions for the application.
"""
from fastapi import Request


def get_engine(request: Request):
    """
    Utility function that returns mongodb engine instance in Fastapi
    :param request:
    :return:
    """
    engine = request.app.engine
    return engine


def get_session(request: Request):
    session = request.app.session
    return session


if __name__ == '__main__':
    pass

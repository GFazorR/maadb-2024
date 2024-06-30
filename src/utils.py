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


def get_ticket_service(request: Request):
    return request.app.ticket_service


def get_event_service(request: Request):
    return request.app.event_service


def get_analytics_service(request: Request):
    return request.app.analytics_service


if __name__ == '__main__':
    pass

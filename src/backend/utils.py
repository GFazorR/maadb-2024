from fastapi import Request


def get_engine(request: Request):
    engine = request.app.engine
    return engine


if __name__ == '__main__':
    pass

from fastapi import APIRouter

router = APIRouter()


# ----------------------- Telemetry --------------------------------
# Persistence (Cassandra)
@router.get('/event/telemetry')
async def read_telemetry():
    pass


@router.get('/profile/attended_events')
async def read_attended_events():
    pass


@router.get('/profile/discount')
async def read_discount():
    pass


if __name__ == '__main__':
    pass

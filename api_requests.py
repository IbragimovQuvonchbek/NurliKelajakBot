import aiohttp

GET_ALL = "http://13.60.228.133/api/v1/olimpiada25082024/get-all25082024/"
GET_BY_TG = "http://13.60.228.133/api/v1/olimpiada25082024/get-bytg25082024/?telegram_id="
ADD_USER = "http://13.60.228.133/api/v1/olimpiada25082024/add25082024/"


async def get_all_request():
    async with aiohttp.ClientSession() as session:
        async with session.get(GET_ALL) as response:
            return await response.json()


async def check_exists(tg_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{GET_BY_TG}{tg_id}") as response:
            return await response.json()


async def add_user(name, grade, phone, telegram_id):
    data = {
        "name": name,
        "grade": grade,
        "phone": phone,
        "telegram_id": telegram_id
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(ADD_USER, json=data) as response:
            return await response.json()

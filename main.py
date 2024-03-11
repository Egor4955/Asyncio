import asyncio
import datetime
from aiohttp import ClientSession
from models import Session, People, Base, engine


async def get_url(url, key, session):
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            return data[key]


async def get_urls(urls, key, session):
    tasks = (asyncio.create_task(get_url(url, key, session)) for url in urls)
    for task in tasks:
        yield await task


async def get_data(urls, key, session):
    data_list = []
    async for data in get_urls(urls, key, session):
        data_list.append(data)
    return ', '.join(data_list)


async def main(people_data):
    async with Session() as session:
        async with ClientSession() as client_session:
            for person in people_data:
                if person is not None:
                    homeworld = await get_data(person['homeworld'], 'name', client_session)
                    films = await get_data(person['films'], 'name', client_session)
                    species = await get_data(person['species'], 'name', client_session)
                    starships = await get_data(person['starships'], 'name', client_session)
                    vehicles = await get_data(person['vehicles'], 'name', client_session)
                    persons = People(
                        birth_year=person['birth_year'],
                        eye_color= person['eye_color'],
                        films=films,
                        gender=person['gender'],
                        hair_color=person['hair_color'],
                        height=person['height'],
                        homeworld=homeworld,
                        mass=person['mass'],
                        name=person['name'],
                        skin_color=person['skin_color'],
                        species=species,
                        starships=starships,
                        vehicles=vehicles,
                    )
                    session.add(person)
                    await session.commit()


async def get_character(people_id: int, session: ClientSession):
    async with session.get(f'https://swapi.dev/api/people/{people_id}') as response:
        if response.status == 200:
            data = await response.json()
            return data
        else:
            return None


async def main2():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
        await connection.commit()

    async with ClientSession() as session:
        list = [get_character(people_id, session) for people_id in range(1, 10)]
        people = await asyncio.gather(*list)
        asyncio.create_task(main(people))

    tasks = set(asyncio.all_tasks()) - {asyncio.current_task()}
    for task in tasks:
        await task


if __name__ == '__main__':
    start = datetime.datetime.now()
    asyncio.run(main2())
    print(datetime.datetime.now() - start)

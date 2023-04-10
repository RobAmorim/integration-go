import requests
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer

#Server
url = 'http://localhost:5000/compute'

#SQLAlchemy engine
engine = create_engine('postgresql://username:password@localhost:5432/database')
meta_data = MetaData()

#table
expression_table = Table(
    'expressions',
    meta_data,
    Column('id', Integer, primary_key=True),
    Column('expression', String)
)

meta_data.create_all(engine)

def test_ingration():
    # valid expression
    expression = '40+3'
    response = requests.post(url, json={'expression': expression}).json()
    assert response['result'] == '43'
    with engine.connect() as conn:
        result = conn.execute(expression_table.select().where(expression_table.c.expression == expression)).fetchone()
    assert result is not None

    # invalid expression
    expression = '6 + Robson'
    response = requests.post(url, json={'expression': expression}).json()
    assert 'error' in response
    with engine.connect() as conn:
        result = conn.execute(expression_table.select().where(expression_table.c.expression == expression)).fetchone()
    assert result is None

    # Test no new rows added to the database since the last valid expression
    with engine.connect() as conn:
        result = conn.execute(expression_table.select().order_by(expression_table.c.id.desc()).limit(2)).fetchall()
    assert len(result) == 2
    assert result[0].expression == '40+3'
    assert result[1].expression != '40+3'

test_ingration() 



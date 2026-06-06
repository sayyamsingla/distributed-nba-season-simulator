import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname='nba_sim',
        user='sayyamsingla',
        password='',
        host='localhost',
        port='5432'
    )

def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS simulation_results (
            id SERIAL PRIMARY KEY,
            season VARCHAR(10),
            champion VARCHAR(100)
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

def save_simulation_result(season, champion):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
    "INSERT INTO simulation_results (season, champion) VALUES (%s, %s)",
    (season, champion)
    )
    conn.commit()
    cursor.close()
    conn.close()

def clear_simulations(season):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM simulation_results WHERE season = %s", (season,))
    conn.commit()
    cursor.close()
    conn.close()

def get_championship_probabilities(season):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
            SELECT champion, COUNT(*) 
            FROM simulation_results 
            WHERE season = %s
            GROUP BY champion
            ORDER BY COUNT(*) DESC
        ''',
        (season,)
    )
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


if __name__ == '__main__':
    create_table()
    print("Table created successfully")




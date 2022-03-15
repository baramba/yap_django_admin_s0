import io

import psycopg2

dsn = {
    'dbname': 'movies_database',
    'user': 'app',
    'password': '123qwe',
    'host': 'localhost',
    'port': 5432,
    'options': '-c search_path=content',
}

with psycopg2.connect(**dsn) as conn, conn.cursor() as cursor:
    # Очищаем таблицу в БД, чтобы загружать данные в пустую таблицу
    cursor.execute("""TRUNCATE content.temp_table""")
    
    # Одиночный insert
    data = ('ca211dbc-a6c6-44a5-b238-39fa16bbfe6c', 'Иван Иванов')
    cursor.execute("""INSERT INTO content.temp_table (id, name) VALUES (%s, %s)""", data)
    
    # Множественный insert
    # Обращаем внимание на подготовку параметров для VALUES через cursor.mogrify
    # Это позволяет без опаски передавать параметры на вставку
    # mogrify позаботится об экранировании и подстановке нужных типов
    # Именно поэтому можно склеить тело запроса с подготовленными параметрами
    data = [
        ('b8531efb-c49d-4111-803f-725c3abc0f5e', 'Василий Васильевич'),
        ('2d5c50d0-0bb4-480c-beab-ded6d0760269', 'Пётр Петрович')
    ]
    args = ','.join(cursor.mogrify("(%s, %s)", item).decode() for item in data)
    cursor.execute(f"""
    INSERT INTO content.temp_table (id, name)
    VALUES {args}
    """)
        
    # Пример использования UPSERT — обновляем уже существующую запись
    data = ('ca211dbc-a6c6-44a5-b238-39fa16bbfe6c', 'Иван Петров')
    cursor.execute("""
    INSERT INTO content.temp_table (id, name)
    VALUES (%s, %s)
    ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name
    """, data)

    cursor.execute("""SELECT name FROM content.temp_table WHERE id = 'ca211dbc-a6c6-44a5-b238-39fa16bbfe6c'""")
    result = cursor.fetchone()
    print('Результат выполнения команды UPSERT ', result)
    
      # Используем команду COPY
    # Для работы COPY требуется взять данные из файла или подготовить файловый объект через io.StringIO
    cursor.execute("""TRUNCATE content.temp_table""")
    data = io.StringIO()
    data.write('ca211dbc-a6c6-44a5-b238-39fa16bbfe6c,Михаил Михайлович')
    data.seek(0)
    cursor.copy_from(data, 'content.temp_table', sep=',', columns=['id', 'name'])

    cursor.execute("""SELECT name FROM content.temp_table WHERE id = 'ca211dbc-a6c6-44a5-b238-39fa16bbfe6c'""")
    result = cursor.fetchone()
    print('Результат выполнения команды COPY ', result)





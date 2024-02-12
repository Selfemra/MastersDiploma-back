import sqlite3
from werkzeug.local import Local, LocalStack

class DBController:
    def __init__(self):
        self.local = Local()
        self.create_tables()

    def get_conn(self):
        if not hasattr(self.local, 'connection'):
            self.local.connection = sqlite3.connect('regions.db')
            self.create_tables()
        return self.local.connection

    def create_tables(self):
        with self.get_conn():
            #self.get_conn().execute('DROP TABLE IF EXISTS people')
           # self.get_conn().execute('DROP TABLE IF EXISTS vaults')
            #self.get_conn().execute('DROP TABLE IF EXISTS streets')
            #self.get_conn().execute('DROP TABLE IF EXISTS cities')
            #self.get_conn().execute('DROP TABLE IF EXISTS regions')

            self.get_conn().execute('''
                CREATE TABLE IF NOT EXISTS regions (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                )
            ''')

            self.get_conn().execute('''
                CREATE TABLE IF NOT EXISTS cities (
                    id INTEGER PRIMARY KEY,
                    region_id INTEGER,
                    name TEXT NOT NULL,
                    FOREIGN KEY (region_id) REFERENCES regions(id)
                )
            ''')

            self.get_conn().execute('''
                CREATE TABLE IF NOT EXISTS streets (
                    id INTEGER PRIMARY KEY,
                    city_id INTEGER,
                    name TEXT NOT NULL,
                    FOREIGN KEY (city_id) REFERENCES cities(id)
                )
            ''')

            self.get_conn().execute('''
                CREATE TABLE IF NOT EXISTS vaults (
                    id INTEGER PRIMARY KEY,
                    street_id INTEGER,
                    name TEXT NOT NULL,
                    FOREIGN KEY (street_id) REFERENCES streets(id)
                )
            ''')

            self.get_conn().execute('''
                CREATE TABLE IF NOT EXISTS people (
                    id INTEGER PRIMARY KEY,
                    vault_id INTEGER,
                    name TEXT NOT NULL,
                    photo_url TEXT,
                    FOREIGN KEY (vault_id) REFERENCES vaults(id),
                    FOREIGN KEY (vault_id) REFERENCES streets(id),  -- Add this line
                    FOREIGN KEY (vault_id) REFERENCES cities(id),   -- Add this line
                    FOREIGN KEY (vault_id) REFERENCES regions(id)   -- Add this line
                )
            ''')

    def get_people_by_vault(self, region, city, street, vault):
        with self.get_conn() as conn:
            cursor = conn.execute('''
                SELECT people.name, people.photo_url
                FROM people
                JOIN vaults ON people.vault_id = vaults.id
                JOIN streets ON vaults.street_id = streets.id
                JOIN cities ON streets.city_id = cities.id
                JOIN regions ON cities.region_id = regions.id
                WHERE regions.name = ? AND cities.name = ? AND streets.name = ? AND vaults.name = ?
            ''', (region, city, street, vault))
            return [{'name': row[0], 'photo_url': row[1]} for row in cursor.fetchall()]


    def get_vault_id(self, region, city, street, vault):
        with self.get_conn():
            cursor = self.get_conn().execute('''
                SELECT vaults.id
                FROM vaults
                JOIN streets ON vaults.street_id = streets.id
                JOIN cities ON streets.city_id = cities.id
                JOIN regions ON cities.region_id = regions.id
                WHERE regions.name = ? AND cities.name = ? AND streets.name = ? AND vaults.name = ?
            ''', (region, city, street, vault))
            result = cursor.fetchone()
            return result[0] if result else None

    def add_person_to_vault_with_photo(self, region, city, street, vault, name, photo_url=None):
        with self.get_conn():
            vault_id = self.get_vault_id(region, city, street, vault)
            self.get_conn().execute('''
                INSERT INTO people (vault_id, name, photo_url)
                VALUES (?, ?, ?)
            ''', (vault_id, name, photo_url))

    def get_all_people(self):
        with self.get_conn() as conn:
            cursor = conn.execute('SELECT id, name, photo_url FROM people')
            people = [{'id': row[0], 'name': row[1], 'photo_url': row[2]} for row in cursor.fetchall()]
            return people

    def remove_person_by_id(self, person_id):
        with self.get_conn() as conn:
            try:
                conn.execute('DELETE FROM people WHERE id = ?', (person_id,))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error removing person with ID {person_id}: {str(e)}")
                conn.rollback()
                return False

    def populate_test_data(self):
        with self.get_conn():
            # Sample regions
            self.get_conn().executemany("INSERT INTO regions (name) VALUES (?)", [('Region',), ('Region2',)])

            # Sample cities
            self.get_conn().executemany("INSERT INTO cities (region_id, name) VALUES (?, ?)", [
                (1, 'City'), (1, 'City2'), (2, 'City3'), (2, 'City4'),
            ])

            # Sample streets
            self.get_conn().executemany("INSERT INTO streets (city_id, name) VALUES (?, ?)", [
                (1, 'Street'), (1, 'Street2'), (2, 'Street3'), (2, 'Street4'),
            ])

            # Sample vaults
            self.get_conn().executemany("INSERT INTO vaults (street_id, name) VALUES (?, ?)", [
                (1, 'Vault'), (1, 'Vault2'), (2, 'Vault3'), (2, 'Vault4'),
            ])

            # Sample people
            #self.get_conn().executemany("INSERT INTO people (vault_id, name, photo_url) VALUES (?, ?, ?)", [
            #    (1, 'Person1', '1.jpg'),
            #    (1, 'Person2', '2.jpg'),
            #    (2, 'Person3', '2.jpg'),
            #    (2, 'Person4', '1.jpg'),
            #])

    def get_all_regions(self):
        with self.get_conn():
            cursor = self.get_conn().execute('SELECT name FROM regions')
            return [row[0] for row in cursor.fetchall()]

    def get_cities_by_region(self, region):
        with self.get_conn():
            cursor = self.get_conn().execute('''
                SELECT cities.name
                FROM cities
                JOIN regions ON cities.region_id = regions.id
                WHERE regions.name = ?
            ''', (region,))
            return [row[0] for row in cursor.fetchall()]

    def get_streets_by_city(self, region, city):
        with self.get_conn():
            cursor = self.get_conn().execute('''
                SELECT streets.name
                FROM streets
                JOIN cities ON streets.city_id = cities.id
                JOIN regions ON cities.region_id = regions.id
                WHERE regions.name = ? AND cities.name = ?
            ''', (region, city))
            return [row[0] for row in cursor.fetchall()]

    def get_vaults_by_street(self, region, city, street):
        with self.get_conn():
            cursor = self.get_conn().execute('''
                SELECT vaults.name
                FROM vaults
                JOIN streets ON vaults.street_id = streets.id
                JOIN cities ON streets.city_id = cities.id
                JOIN regions ON cities.region_id = regions.id
                WHERE regions.name = ? AND cities.name = ? AND streets.name = ?
            ''', (region, city, street))
            return [row[0] for row in cursor.fetchall()]

    def get_people_by_address(self, region, city, street, vault):
        with self.get_conn():
            cursor = self.get_conn().execute('''
                SELECT people.id, people.name, people.photo_url
                FROM people
                JOIN vaults ON people.vault_id = vaults.id
                JOIN streets ON vaults.street_id = streets.id
                JOIN cities ON streets.city_id = cities.id
                JOIN regions ON cities.region_id = regions.id
                WHERE regions.name = ? AND cities.name = ? AND streets.name = ? AND vaults.name = ?
            ''', (region, city, street, vault))
            return [{'id': row[0], 'name': row[1], 'photo_url': row[2]} for row in cursor.fetchall()]



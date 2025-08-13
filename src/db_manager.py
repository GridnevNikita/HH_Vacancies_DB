from typing import Any, Dict, List, Optional

import psycopg2


class DBManager:
    """
    Класс для управления базой данных PostgreSQL с компаниями и вакансиями.
    """

    def __init__(
        self,
        dbname: str,
        user: str,
        password: str,
        host: str = "localhost",
        port: int = 5432,
    ) -> None:
        """Инициализация подключения к базе данных."""
        self.connection = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)

    def create_tables(self) -> None:
        """Создает таблицы companies и vacancies в базе данных."""
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS companies (
                    id SERIAL PRIMARY KEY,
                    employer_id INT UNIQUE NOT NULL,
                    name VARCHAR,
                    url VARCHAR
                );
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS vacancies (
                    id SERIAL PRIMARY KEY,
                    vacancy_id INT UNIQUE NOT NULL,
                    employer_id INT NOT NULL REFERENCES companies(employer_id),
                    name VARCHAR,
                    url VARCHAR,
                    salary_from INT,
                    salary_to INT,
                    currency VARCHAR,
                    description VARCHAR
                );
            """
            )
        self.connection.commit()

    def insert_company(self, employer_id: int, name: str, url: Optional[str] = None) -> None:
        """Вставляет информацию о компании в таблицу companies."""
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO companies (employer_id, name, url)
                VALUES (%s, %s, %s)
                ON CONFLICT (employer_id) DO NOTHING;
            """,
                (employer_id, name, url),
            )
        self.connection.commit()

    def insert_vacancy(
        self,
        vacancy_id: int,
        employer_id: int,
        name: str,
        url: Optional[str] = None,
        salary_from: Optional[int] = None,
        salary_to: Optional[int] = None,
        currency: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """Вставляет информацию о вакансии в таблицу vacancies."""
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO vacancies (vacancy_id, employer_id, name, url,
                 salary_from, salary_to, currency, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (vacancy_id) DO NOTHING;
            """,
                (vacancy_id, employer_id, name, url, salary_from, salary_to, currency, description),
            )
        self.connection.commit()

    def get_companies_and_vacancies_count(self) -> List[tuple[Any, ...]]:
        """Получает список компаний и количество вакансий у каждой компании."""
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT c.name, COUNT(v.id) AS vacancy_count
                FROM companies c
                LEFT JOIN vacancies v ON c.employer_id = v.employer_id
                GROUP BY c.name
                ORDER BY vacancy_count DESC;
            """
            )
            return cursor.fetchall()

    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """Получает список всех вакансий с информацией о компании, названии, зарплате и ссылке."""
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT c.name AS company_name, v.name AS vacancy_name,
                       v.salary_from, v.salary_to, v.currency, v.url
                FROM vacancies v
                JOIN companies c ON v.employer_id = c.employer_id;
            """
            )
            rows = cursor.fetchall()
            vacancies = []
            for row in rows:
                vacancies.append(
                    {
                        "company_name": row[0],
                        "vacancy_name": row[1],
                        "salary_from": row[2],
                        "salary_to": row[3],
                        "currency": row[4],
                        "url": row[5],
                    }
                )
            return vacancies

    def get_avg_salary(self) -> Optional[float]:
        """Получает среднюю зарплату по вакансиям."""
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT ROUND(AVG((salary_from + salary_to) / 2.0), 2)
                FROM vacancies
                WHERE salary_from IS NOT NULL AND salary_to IS NOT NULL;
            """
            )
            result = cursor.fetchone()
            return result[0] if result else None

    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        """Получает вакансии с зарплатой выше средней по всем вакансиям."""
        avg_salary = self.get_avg_salary()
        if avg_salary is None:
            return []
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT c.name, v.name, v.salary_from, v.salary_to, v.currency, v.url
                FROM vacancies v
                JOIN companies c ON v.employer_id = c.employer_id
                WHERE ((v.salary_from + v.salary_to) / 2.0) > %s;
            """,
                (avg_salary,),
            )
            rows = cursor.fetchall()
            return [
                {
                    "company_name": row[0],
                    "vacancy_name": row[1],
                    "salary_from": row[2],
                    "salary_to": row[3],
                    "currency": row[4],
                    "url": row[5],
                }
                for row in rows
            ]

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Получает вакансии, в названии которых содержится заданное ключевое слово."""
        like_pattern = f"%{keyword.lower()}%"
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT c.name, v.name, v.salary_from, v.salary_to, v.currency, v.url
                FROM vacancies v
                JOIN companies c ON v.employer_id = c.employer_id
                WHERE LOWER(v.name) LIKE %s;
            """,
                (like_pattern,),
            )
            rows = cursor.fetchall()
            return [
                {
                    "company_name": row[0],
                    "vacancy_name": row[1],
                    "salary_from": row[2],
                    "salary_to": row[3],
                    "currency": row[4],
                    "url": row[5],
                }
                for row in rows
            ]

    def close(self) -> None:
        """Закрывает соединение с базой данных."""
        self.connection.close()

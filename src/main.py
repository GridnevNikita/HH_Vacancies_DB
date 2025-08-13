import os

import psycopg2
from dotenv import load_dotenv

from src.api_hh import HeadHunterAPI
from src.db_create import load_companies_and_vacancies
from src.db_manager import DBManager


def create_database_if_not_exists(dbname, user, password, host="localhost", port=5432):
    """Создаёт базу данных, если её ещё нет."""
    conn = psycopg2.connect(dbname="postgres", user=user, password=password, host=host, port=port)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (dbname,))
            exists = cursor.fetchone()
            if not exists:
                cursor.execute(f"CREATE DATABASE {dbname};")
                conn.commit()
                print(f"База данных '{dbname}' создана.")
            else:
                print(f"База данных '{dbname}' уже существует.")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def main():
    """Главная функция"""
    load_dotenv()

    dbname = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", 5432))

    create_database_if_not_exists(dbname, user, password, host, port)
    db = DBManager(dbname=dbname, user=user, password=password, host=host, port=port)

    api = HeadHunterAPI()
    company_ids = [15478, 3529, 1740, 78638, 1057, 3776, 80, 39209, 2748, 2180]

    while True:
        print("\n=== Меню ===")
        print("1. Загрузить компании и вакансии в базу")
        print("2. Показать компании и количество вакансий")
        print("3. Показать все вакансии")
        print("4. Показать среднюю зарплату")
        print("5. Показать вакансии с зарплатой выше средней")
        print("6. Поиск вакансий по ключевому слову")
        print("0. Выход")

        choice = input("Выберите действие: ")

        if choice == "1":
            db.create_tables()
            load_companies_and_vacancies(db, api, company_ids)
            print("Данные успешно загружены в базу.")
        elif choice == "2":
            for company, count in db.get_companies_and_vacancies_count():
                print(f"{company}: {count}")
        elif choice == "3":
            for vac in db.get_all_vacancies():
                print(
                    f"{vac['vacancy_name']} в {vac['company_name']} "
                    f"- {vac['salary_from']}-{vac['salary_to']} {vac['currency']}\n"
                    f"Ссылка: {vac['url']}"
                )
                print("-" * 40)
        elif choice == "4":
            print(f"Средняя зарплата: {db.get_avg_salary()}")

        elif choice == "5":
            for vac in db.get_vacancies_with_higher_salary():
                print(
                    f"{vac['vacancy_name']} в {vac['company_name']} "
                    f"- {vac['salary_from']}-{vac['salary_to']} {vac['currency']}\n"
                    f"Ссылка: {vac['url']}"
                )
                print("-" * 40)

        elif choice == "6":
            keyword = input("Введите ключевое слово: ")
            for vac in db.get_vacancies_with_keyword(keyword):
                print(
                    f"{vac['vacancy_name']} в {vac['company_name']} "
                    f"- {vac['salary_from']}-{vac['salary_to']} {vac['currency']}\n"
                    f"Ссылка: {vac['url']}"
                )
                print("-" * 40)
        elif choice == "0":
            db.close()
            print("Выход из программы.")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()

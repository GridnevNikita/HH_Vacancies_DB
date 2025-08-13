from typing import List
from api_hh import HeadHunterAPI
from db_manager import DBManager


def load_companies_and_vacancies(db: DBManager, api: HeadHunterAPI, company_ids: List[int]) -> None:
    """
    Загружает информацию о компаниях и их вакансиях в базу.
    """
    for employer_id in company_ids:
        # Получаем данные о компании
        company_info = api.get_company_info(employer_id)
        db.insert_company(
            employer_id=company_info["id"],
            name=company_info["name"],
            url=company_info.get("site_url")
        )

        # Получаем вакансии компании
        vacancies = api.get_vacancies_for_company(employer_id)
        for vac in vacancies:
            salary = vac.get("salary")
            salary_from = salary.get("from") if salary else None
            salary_to = salary.get("to") if salary else None
            currency = salary.get("currency") if salary else None

            db.insert_vacancy(
                vacancy_id=vac["id"],
                employer_id=employer_id,
                name=vac["name"],
                url=vac.get("alternate_url"),
                salary_from=salary_from,
                salary_to=salary_to,
                currency=currency,
                description=vac.get("snippet", {}).get("responsibility")
            )
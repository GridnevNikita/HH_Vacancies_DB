from typing import Any, Dict, List, Optional

import requests


class HeadHunterAPI:
    """
    Класс для работы с API hh.ru.
    """

    def __init__(self, base_url: str = "https://api.hh.ru"):
        self.__base_url = base_url

    def _get_json(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Общий метод GET-запроса к API."""
        url = f"{self.__base_url}{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_company_info(self, employer_id: int) -> Dict[str, Any]:
        """Получение информации о компании."""
        endpoint = f"/employers/{employer_id}"
        return self._get_json(endpoint)

    def get_vacancies_for_company(self, employer_id: int, per_page: int = 100) -> List[Dict[str, Any]]:
        """Получение вакансий для одной компании."""
        vacancies = []
        page = 0

        while True:
            params = {"employer_id": employer_id, "per_page": per_page, "page": page, "area": 1}
            data = self._get_json("/vacancies", params)
            items = data.get("items", [])
            vacancies.extend(items)
            if page >= data.get("pages", 0) - 1:
                break
            page += 1
        return vacancies

    def get_vacancies_for_companies(self, employer_ids: List[int]) -> Dict[int, List[Dict[str, Any]]]:
        """
        Получение вакансий для списка компаний.
        Возвращает словарь employer_id -> список вакансий.
        """
        result = {}
        for eid in employer_ids:
            result[eid] = self.get_vacancies_for_company(eid)
        return result

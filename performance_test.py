import random
import uuid
from locust import HttpUser, task, between

# Тестовые данные
TEAM_NAME = "loadtest_team"
USER_IDS = ["1", "2", "3", "4", "5"]

class PRUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """
        Создаем команду при старте.
        Если команда уже есть (ошибка 400), игнорируем ошибку и помечаем запрос как успешный.
        """
        payload = {
            "team_name": TEAM_NAME,
            "members": [
                {"user_id": uid, "username": f"User_{uid}", "is_active": True} 
                for uid in USER_IDS
            ]
        }
        
        with self.client.post("/team/add", json=payload, catch_response=True) as response:
            if response.status_code == 201:
                response.success()  
            elif response.status_code == 400 and "TEAM_EXISTS" in response.text:
                response.success()  
            else:
                response.failure(f"Unexpected error: {response.text}")
    @task(3) 
    def view_reviews(self):
        """Пользователь проверяет, назначили ли на него ревью"""
        user_id = random.choice(USER_IDS)
        self.client.get(f"/pullRequest/getReview?user_id={user_id}")

    @task(1)
    def create_pr(self):
        """Пользователь создает PR"""
        author_id = random.choice(USER_IDS)
        pr_id = f"pr-{uuid.uuid4()}"
        
        self.client.post("/pullRequest/create", json={
            "pull_request_id": pr_id,
            "pull_request_name": f"Load Test PR {pr_id}",
            "author_id": author_id
        })

    @task(1)
    def view_stats(self):
        """Админ смотрит статистику"""
        self.client.get("/stats")

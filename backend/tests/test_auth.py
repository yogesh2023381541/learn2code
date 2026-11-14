def signup_payload() -> dict[str, str]:
    return {
        "full_name": "Test Learner",
        "email": "learner@example.com",
        "password": "correct horse battery staple",
    }


def test_signup_returns_tokens_and_me_is_protected(client):
    response = client.post("/api/auth/signup", json=signup_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["user"]["email"] == "learner@example.com"
    assert client.get("/api/auth/me").status_code == 401
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200
    assert me.json()["profile"]["subjects"] == []


def test_login_refresh_rotates_and_logout_revokes(client):
    client.post("/api/auth/signup", json=signup_payload())
    login = client.post(
        "/api/auth/login",
        json={"email": "learner@example.com", "password": signup_payload()["password"]},
    )
    assert login.status_code == 200
    old_refresh = login.json()["refresh_token"]

    refreshed = client.post("/api/auth/refresh", json={"refresh_token": old_refresh})
    assert refreshed.status_code == 200
    new_refresh = refreshed.json()["refresh_token"]
    assert new_refresh != old_refresh
    assert client.post("/api/auth/refresh", json={"refresh_token": old_refresh}).status_code == 401

    assert client.post("/api/auth/logout", json={"refresh_token": new_refresh}).status_code == 204
    assert client.post("/api/auth/refresh", json={"refresh_token": new_refresh}).status_code == 401


def test_onboarding_is_persisted_for_authenticated_user(client):
    signup = client.post("/api/auth/signup", json=signup_payload()).json()
    headers = {"Authorization": f"Bearer {signup['access_token']}"}
    response = client.put(
        "/api/users/me/onboarding",
        headers=headers,
        json={
            "experience_level": "beginner",
            "learning_goal": "Learn Programming",
            "preferred_language": "Python",
            "daily_minutes": 30,
            "subjects": ["Python", "React"],
        },
    )

    assert response.status_code == 200
    assert response.json()["profile"]["learning_goal"] == "Learn Programming"
    assert response.json()["profile"]["subjects"] == ["Python", "React"]
    dashboard = client.get("/api/dashboard", headers=headers)
    assert dashboard.status_code == 200
    assert dashboard.json()["overall_progress"] == 0
    assert [subject["name"] for subject in dashboard.json()["recommended_subjects"]] == ["Python", "React"]


def test_activity_updates_dashboard_metrics(client):
    signup = client.post("/api/auth/signup", json=signup_payload()).json()
    headers = {"Authorization": f"Bearer {signup['access_token']}"}

    activity = client.post(
        "/api/users/me/activity",
        headers=headers,
        json={"minutes": 45, "activity_type": "lesson"},
    )

    assert activity.status_code == 201
    dashboard = client.get("/api/dashboard", headers=headers)
    assert dashboard.json()["learning_hours"] == 0.75
    assert dashboard.json()["topics_completed"] == 1
    assert dashboard.json()["today_minutes"] == 45
    assert sum(dashboard.json()["weekly_activity"]) == 45


def test_lessons_completion_updates_progress_and_history(client):
    signup = client.post("/api/auth/signup", json=signup_payload()).json()
    headers = {"Authorization": f"Bearer {signup['access_token']}"}
    client.put(
        "/api/users/me/onboarding",
        headers=headers,
        json={
            "experience_level": "beginner",
            "learning_goal": "Learn Programming",
            "preferred_language": "Python",
            "daily_minutes": 30,
            "subjects": ["Python"],
        },
    )
    lessons = client.get("/api/subjects/python/lessons", headers=headers)
    assert lessons.status_code == 200
    lesson = lessons.json()[0]
    assert lesson["completed"] is False
    completed = client.post(f"/api/lessons/{lesson['id']}/complete", headers=headers)
    assert completed.status_code == 200
    assert completed.json()["completed"] is True
    assert client.get("/api/subjects/python/lessons", headers=headers).json()[0]["completed"] is True
    assert client.get("/api/users/me/history", headers=headers).status_code == 200


def test_practice_submission_and_bookmark_are_persisted(client):
    signup = client.post("/api/auth/signup", json=signup_payload()).json()
    headers = {"Authorization": f"Bearer {signup['access_token']}"}
    problems = client.get("/api/practice/problems", headers=headers)
    assert problems.status_code == 200
    problem = problems.json()[0]
    submission = client.post(
        f"/api/practice/problems/{problem['id']}/submissions",
        headers=headers,
        json={"language": "python", "code": "return answer"},
    )
    assert submission.status_code == 201
    assert submission.json()["status"] == "accepted"
    assert client.get("/api/practice/problems", headers=headers).json()[0]["solved"] is True
    bookmark = client.post(
        "/api/users/me/bookmarks",
        headers=headers,
        json={"target_type": "problem", "target_id": problem["id"]},
    )
    assert bookmark.status_code == 201
    assert len(client.get("/api/users/me/bookmarks", headers=headers).json()) == 1


def test_ai_conversations_are_private_and_provider_errors_are_explicit(client):
    first = client.post("/api/auth/signup", json=signup_payload()).json()
    second = client.post(
        "/api/auth/signup",
        json={"full_name": "Other Learner", "email": "other@example.com", "password": "correct horse battery staple"},
    ).json()
    first_headers = {"Authorization": f"Bearer {first['access_token']}"}
    second_headers = {"Authorization": f"Bearer {second['access_token']}"}
    conversation = client.post(
        "/api/ai/conversations",
        headers=first_headers,
        json={"title": "Python help", "teaching_mode": "beginner"},
    )
    assert conversation.status_code == 201
    conversation_id = conversation.json()["id"]
    assert client.get(f"/api/ai/conversations/{conversation_id}", headers=second_headers).status_code == 404
    message = client.post(
        f"/api/ai/conversations/{conversation_id}/messages",
        headers=first_headers,
        json={"content": "Explain functions", "context": {"subject": "Python"}},
    )
    assert message.status_code == 503
    assert "AI_PROVIDER_URL" in message.json()["detail"]

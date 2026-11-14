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

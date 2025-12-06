import urllib.request
import json

base_url = "http://localhost:8001"

def test_get_root():
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("GET /: PASS -", response.json())
            return True
        else:
            print(f"GET /: FAIL - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"GET /: ERROR - {e}")
        return False

def test_post_disorder():
    data = {
        "name": "Anxiety Disorder",
        "description": "A mental health condition characterized by excessive worry.",
        "symptoms": "Restlessness, rapid heartbeat, sweating"
    }
    try:
        response = requests.post(f"{base_url}/disorder", json=data)
        if response.status_code == 200:
            print("POST /disorder: PASS -", response.json())
            return True
        else:
            print(f"POST /disorder: FAIL - Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print(f"POST /disorder: ERROR - {e}")
        return False

def test_get_disorders():
    try:
        response = requests.get(f"{base_url}/disorder")
        if response.status_code == 200:
            disorders = response.json()
            print(f"GET /disorder: PASS - Retrieved {len(disorders)} disorders")
            if disorders:
                return disorders[0]['id']  # Return first disorder ID for further tests
            return None
        else:
            print(f"GET /disorder: FAIL - Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"GET /disorder: ERROR - {e}")
        return None

def test_get_single_disorder(disorder_id):
    if not disorder_id:
        print("GET /disorder/{id}: SKIP - No disorder ID available")
        return False
    try:
        response = requests.get(f"{base_url}/disorder/{disorder_id}")
        if response.status_code == 200:
            print("GET /disorder/{id}: PASS -", response.json())
            return True
        else:
            print(f"GET /disorder/{id}: FAIL - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"GET /disorder/{id}: ERROR - {e}")
        return False

def test_patch_disorder(disorder_id):
    if not disorder_id:
        print("PATCH /disorder/{id}: SKIP - No disorder ID available")
        return False
    data = {
        "name": "Updated Anxiety Disorder",
        "description": "Updated description.",
        "symptoms": "Updated symptoms"
    }
    try:
        response = requests.patch(f"{base_url}/disorder/{disorder_id}", json=data)
        if response.status_code == 200:
            print("PATCH /disorder/{id}: PASS -", response.json())
            return True
        else:
            print(f"PATCH /disorder/{id}: FAIL - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"PATCH /disorder/{id}: ERROR - {e}")
        return False

def test_delete_disorder(disorder_id):
    if not disorder_id:
        print("DELETE /disorder/{id}: SKIP - No disorder ID available")
        return False
    try:
        response = requests.delete(f"{base_url}/disorder/{disorder_id}")
        if response.status_code == 200:
            print("DELETE /disorder/{id}: PASS -", response.json())
            return True
        else:
            print(f"DELETE /disorder/{id}: FAIL - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"DELETE /disorder/{id}: ERROR - {e}")
        return False

def test_post_assessment():
    data = {
        "session_id": "session123",
        "answers": "yes,no,yes",
        "result": "medium",
        "severity_score": 3,
        "disorder_id": 1
    }
    try:
        response = requests.post(f"{base_url}/assessment", json=data)
        if response.status_code == 200:
            print("POST /assessment: PASS -", response.json())
            return True
        else:
            print(f"POST /assessment: FAIL - Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print(f"POST /assessment: ERROR - {e}")
        return False

def test_get_assessments():
    try:
        response = requests.get(f"{base_url}/assessment")
        if response.status_code == 200:
            assessments = response.json()
            print(f"GET /assessment: PASS - Retrieved {len(assessments)} assessments")
            if assessments:
                return assessments[0]['id']  # Return first assessment ID
            return None
        else:
            print(f"GET /assessment: FAIL - Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"GET /assessment: ERROR - {e}")
        return None

def test_get_single_assessment(assessment_id):
    if not assessment_id:
        print("GET /assessment/{id}: SKIP - No assessment ID available")
        return False
    try:
        response = requests.get(f"{base_url}/assessment/{assessment_id}")
        if response.status_code == 200:
            print("GET /assessment/{id}: PASS -", response.json())
            return True
        else:
            print(f"GET /assessment/{id}: FAIL - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"GET /assessment/{id}: ERROR - {e}")
        return False

def test_patch_assessment(assessment_id):
    if not assessment_id:
        print("PATCH /assessment/{id}: SKIP - No assessment ID available")
        return False
    data = {
        "session_id": "session123",
        "answers": "yes,no,no",
        "result": "low",
        "severity_score": 2,
        "disorder_id": 1
    }
    try:
        response = requests.patch(f"{base_url}/assessment/{assessment_id}", json=data)
        if response.status_code == 200:
            print("PATCH /assessment/{id}: PASS -", response.json())
            return True
        else:
            print(f"PATCH /assessment/{id}: FAIL - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"PATCH /assessment/{id}: ERROR - {e}")
        return False

def test_delete_assessment(assessment_id):
    if not assessment_id:
        print("DELETE /assessment/{id}: SKIP - No assessment ID available")
        return False
    try:
        response = requests.delete(f"{base_url}/assessment/{assessment_id}")
        if response.status_code == 200:
            print("DELETE /assessment/{id}: PASS -", response.json())
            return True
        else:
            print(f"DELETE /assessment/{id}: FAIL - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"DELETE /assessment/{id}: ERROR - {e}")
        return False

if __name__ == "__main__":
    print("Starting endpoint tests...")

    # Test root
    test_get_root()

    # Test disorder endpoints
    disorder_id = None
    test_post_disorder()
    disorder_id = test_get_disorders()
    test_get_single_disorder(disorder_id)
    test_patch_disorder(disorder_id)
    test_delete_disorder(disorder_id)

    # Test assessment endpoints
    assessment_id = None
    test_post_assessment()
    assessment_id = test_get_assessments()
    test_get_single_assessment(assessment_id)
    test_patch_assessment(assessment_id)
    test_delete_assessment(assessment_id)

    print("Endpoint tests completed.")

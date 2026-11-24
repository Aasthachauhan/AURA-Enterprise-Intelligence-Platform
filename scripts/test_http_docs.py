import requests

login_res = requests.post(
    "http://127.0.0.1:8000/api/v1/auth/login",
    json={"email": "admin@aura.enterprise", "password": "admin123"}
)
print("Login status:", login_res.status_code)
token_data = login_res.json()
token = token_data["access_token"]
ws_id = token_data["user"].get("active_workspace_id")
print("Active WS in login:", ws_id)

headers = {"Authorization": f"Bearer {token}", "X-Workspace-Id": ws_id}
doc_res = requests.get("http://127.0.0.1:8000/api/v1/documents", headers=headers)
print("GET /documents status:", doc_res.status_code)
data = doc_res.json()
print("Total returned:", data.get("total"))
print("Items count:", len(data.get("items", [])))
for item in data.get("items", []):
    print(" -", item.get("title"), item.get("file_type"), item.get("status"))

# Also test GET /api/v1/workspaces
ws_res = requests.get("http://127.0.0.1:8000/api/v1/workspaces", headers=headers)
print("GET /workspaces status:", ws_res.status_code)
print("Workspaces list:", [(w["name"], w["id"]) for w in ws_res.json()])

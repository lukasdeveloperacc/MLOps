import kfp
import requests

HOST = "http://localhost:8080"          # (Ingress/Gateway) 포워딩 주소
NAMESPACE = "kubeflow"
USERNAME = "user@example.com"
PASSWORD = "12341234"

s = requests.Session()
r = s.get(HOST, allow_redirects=True)
response = s.post(r.url, data={"login": USERNAME, "password": PASSWORD}, allow_redirects=True)
print(response.status_code)
print(response.text)
session_cookie = s.cookies.get("authservice_session")
if not session_cookie:
    raise RuntimeError("authservice_session 쿠키를 못 얻었습니다.")

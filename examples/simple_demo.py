from resilient_http.session import ResilientRequestsSession

s = ResilientRequestsSession()
r = s.get("https://httpbin.org/status/503")
print(r.status_code)

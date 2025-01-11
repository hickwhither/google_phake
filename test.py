from urllib.parse import urljoin

def resolve_url(origin, url):
    # Xử lý URL bằng cách kết hợp origin và url
    resolved_url = urljoin(origin, url)
    return resolved_url

# Ví dụ sử dụng
origin = "https://hackmd.io/deptr"
url1 = "/asd/asd"
url2 = "./asd/asd"
url3 = "https://example.com/asd/asd"

print(resolve_url(origin, url1))  # Kết quả: https://hackmd.io/asd/asd
print(resolve_url(origin, url2))  # Kết quả: https://hackmd.io/deptr/asd/asd
print(resolve_url(origin, url3))  # Kết quả: https://example.com/asd/asd

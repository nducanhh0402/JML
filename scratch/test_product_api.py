import json, sys, urllib.request, urllib.error
BASE = 'http://127.0.0.1:8000'

def http_request(method, path, data=None, token=None):
    url = BASE + path
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    if data is not None:
        body = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    else:
        body = None
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            resp_body = resp.read().decode('utf-8')
            return resp.getcode(), resp_body
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except Exception as e:
        return None, str(e)

def login_admin():
    code, body = http_request('POST', '/api/auth/login', {'username':'admin','password':'123456'})
    if code == 200:
        data = json.loads(body)
        return data.get('access_token')
    return None

admin_token = login_admin()
print('Admin token fetched:', bool(admin_token))

results = []
# 1. Create valid product
payload = {
    'title':'Test Product',
    'category':'tech',
    'price':100000,
    'stock':10,
    'status':'approved'
}
code, body = http_request('POST', '/api/admin/products', payload, admin_token)
results.append(('Create valid', code, body))
prod_id = None
if code == 200:
    try:
        prod_id = json.loads(body).get('id')
    except:
        pass
# 2. Create negative price
payload2 = {'title':'Bad Price','category':'tech','price':-5000,'stock':5}
code2, body2 = http_request('POST', '/api/admin/products', payload2, admin_token)
results.append(('Create negative price', code2, body2))
# 3. Update non-existent
code3, body3 = http_request('PUT', '/api/admin/products/99999', {'title':'Updated'}, admin_token)
results.append(('Update missing', code3, body3))
# 4. Delete valid product if created
if prod_id:
    code4, body4 = http_request('DELETE', f'/api/admin/products/{prod_id}', None, admin_token)
    results.append(('Delete valid', code4, body4))
else:
    results.append(('Delete valid', 'skip', 'no product created'))
# 5. Delete category with products (assume category tech exists and has products)
code5, body5 = http_request('DELETE', '/api/admin/categories/tech', None, admin_token)
results.append(('Delete category with products', code5, body5))
# 6. Non-admin access (use buyer token placeholder - attempt without token gives 401)
code6, body6 = http_request('GET', '/api/admin/products', None, None)
results.append(('Access without token', code6, body6))
# 7. Access with wrong role (login as buyer)
# attempt login as buyer (assume username buyer, password 123456)
code7, body7 = http_request('POST', '/api/auth/login', {'username':'buyer','password':'123456'})
buyer_token = None
if code7 == 200:
    buyer_token = json.loads(body7).get('access_token')
code7b, body7b = http_request('GET', '/api/admin/products', None, buyer_token)
results.append(('Non-admin access', code7b, body7b))

for name, c, b in results:
    print(f'[{name}] Status: {c}\nResponse: {b}\n')

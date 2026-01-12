
from router.app import create_app
app = create_app()

print("--- ROUTE MAP ---")
for route in app.routes:
    print(f"{route.path} [{route.name}]")

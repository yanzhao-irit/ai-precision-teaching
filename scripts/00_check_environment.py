import sys

print("Python:", sys.version)

modules = ["pandas", "neo4j", "dotenv", "networkx"]
for name in modules:
    try:
        __import__(name)
        print(f"OK: {name}")
    except Exception as e:
        print(f"MISSING: {name} -> {e}")

print("\nIf all modules are OK, the Python environment is ready.")

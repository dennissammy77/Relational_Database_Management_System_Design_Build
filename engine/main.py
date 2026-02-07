import sys
import os

# Add the parent directory to sys.path to allow importing 'engine' as a package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.normalizer.normalizer import Normalizer

def main():
    normalizer = Normalizer("SELECT * FROM users WHERE active = true")
    result = normalizer.normalize()
    print(f"Normalization Result: {result}")
    create_normalizer = Normalizer("CREATE TABLE users (id INT, name TEXT, active BOOLEAN)")
    create_result = create_normalizer.normalize()
    print(f"Create Normalization Result: {create_result}")

if __name__ == "__main__":
    main()
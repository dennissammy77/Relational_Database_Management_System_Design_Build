from normalizer import Normalizer

def main():
    normalizer = Normalizer("SELECT * FROM users WHERE id = 1")
    normalizer.normalize()

if __name__ == "__main__":
    main()
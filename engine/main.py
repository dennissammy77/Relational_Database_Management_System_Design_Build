from normalizer import Normalizer

def main():
    normalizer = Normalizer("SELECT * FROM users WHERE active = true")
    normalizer.normalize()

if __name__ == "__main__":
    main()
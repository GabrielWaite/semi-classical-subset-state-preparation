from utils.grover_rudolph_angles import GroverRudolphAngles as gra

def main():
    x = gra(6)
    print(x)
    print(x.multi_control_prefixes)

if __name__ == "__main__":
    main()
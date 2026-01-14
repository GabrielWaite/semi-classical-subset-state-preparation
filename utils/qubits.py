import cirq

class QubitRegister:
    def __init__(self, count: int, prefix: str = 'x'):
        if count < 0:
            raise ValueError(f"Qubit count cannot be negative (received {count}).")
        
        self.count = count
        self.prefix = prefix
        self.qubits = [cirq.NamedQubit(f'{prefix}{i}') for i in range(count)]
        
    def __getitem__(self, key):
        """Allows you to do register[0] instead of register.qubits[0]"""
        return self.qubits[key]

    def __len__(self):
        return self.count

    def __iter__(self):
        return iter(self.qubits)
    
def main():
    """Example usage of QubitRegister"""
    qr = QubitRegister(4, prefix='q')
    print(f"Qubit Register of size {len(qr)}: {qr.qubits}")

if __name__ == "__main__":
    main()
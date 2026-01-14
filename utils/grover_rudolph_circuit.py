import math
from dataclasses import dataclass, field
import cirq
import numpy as np

from utils.grover_rudolph_angles import GroverRudolphAngles

class ControlTag:
    def __init__(self, cardinality: int):
        self.cardinality = cardinality
        self.group_number = math.ceil(np.log2(cardinality)) - 1 # indexing: starts at 0
        self.position_in_group = (cardinality - 1) - 2**self.group_number # indexing: starts at 0
        self.binary_signature = f"{self.position_in_group:0{self.group_number}b}" # binary representation with leading zeros
        self.control_signature = [(int(i),) for i in self.binary_signature] # tuple representation for cirq

    @classmethod
    def generate_range(cls, max_cardinality: int, start_at: int = 3) -> list[tuple[int, 'ControlTag']]:
        """Factory method to generate a sequence of ControlTags."""
        if max_cardinality < start_at:
            return []
        
        return [(c, cls(c)) for c in range(start_at, max_cardinality + 1)]

# then to get the group_number use:
# >>> ctg = ControlTagGenerator(cardinality)
# >>> ctg.group_number

@dataclass
class GroverRudolphCircuit:
    """
    A class to generate a Grover-Rudolph circuit for a given cardinality.
    The circuit prepares a uniform superposition of all subsets of size `cardinality`.
    """
    cardinality: int
    num_qubits: int
    tag_range: list[tuple[int, ControlTag]] = field(init=False)
    angles: list[float] = field(init=False)

    def __post_init__(self):
        if self.cardinality <= 2: raise ValueError("Cardinality must be greater than 2.")
        if self.num_qubits <= 0 or self.num_qubits < math.ceil(np.log2(self.cardinality)): raise ValueError("Too few qubits!")
        self.tag_range = ControlTag.generate_range(self.cardinality)
        self.angles = GroverRudolphAngles(self.cardinality).angles

    @property
    def data_qubits(self) -> list[cirq.NamedQubit]:
        qubits = [cirq.NamedQubit(f'x{i}') for i in range(self.num_qubits)]
        return qubits[::-1] # reverse the qubits for consistency with our convention.
        # cirq uses little-endian ordering, so we reverse the qubits to match our

    def generate_circuit(self) -> cirq.Circuit:
        circuit: cirq.Circuit = cirq.Circuit()

        if self.cardinality == 2:
            circuit.append(cirq.Ry(rads=self.angles[0]).on(self.data_qubits[0]))
        else:
            circuit.append(cirq.Ry(rads=self.angles[0]).on(self.data_qubits[0]))
            for step in range(3, self.cardinality + 1):
                shift_step: int = step - 3
                ctrl_tag: ControlTag = self.tag_range[shift_step][1]

                ctrl_qb_group: list[cirq.NamedQubit] = self.data_qubits[:ctrl_tag.group_number] # identify the ctrl qbs
                target_qb: cirq.NamedQubit = self.data_qubits[ctrl_tag.group_number] # identify the target qb
                angle: float = self.angles[step - 2] # define the angle

                # initialise the ctrl ry gate
                ctrl_ry_gate: cirq.Gate = cirq.Ry(rads=angle).controlled(
                    num_controls=ctrl_tag.group_number,
                    control_values=ctrl_tag.control_signature
                )
                circuit.append(ctrl_ry_gate.on(*ctrl_qb_group, target_qb))

        return circuit

@dataclass
class GroverRudolphGate(cirq.Gate):
    cardinality: int
    num_qubits: int
    
    def __post_init__(self):
        if self.cardinality <= 2: raise ValueError("Cardinality must be greater than 2 for generating gate.")
        if self.num_qubits <= 0 or self.num_qubits < math.ceil(np.log2(self.cardinality)): raise ValueError("Too few qubits!")

    def _num_qubits_(self) -> int:
        """
        Return the number of qubits required for the Grover-Rudolph gate.
        This is equal to the number of qubits plus one ancilla qubit.
        """
        return self.num_qubits
    
    def _decompose_(self, qubits: list[cirq.Qid]) -> cirq.OP_TREE:
        if len(qubits) != self.num_qubits: raise ValueError(f"Expected {self.num_qubits} qubits, but got {len(qubits)}.")
        
        # Generate the circuit as operations
        gr_circuit = GroverRudolphCircuit(cardinality=self.cardinality, num_qubits=self.num_qubits)
        yield from gr_circuit.generate_circuit().all_operations()

def main():
    """Example"""
    c = 6
    angle_generator = GroverRudolphAngles(c)
    print(angle_generator)
    binary_control_sequence = angle_generator.multi_control_prefixes

    print(f"Cardinality: {c}")
    print(f"Binary Control Sequence: {binary_control_sequence}")
    print(f"Expect {c - 1} angles, with {c - 2} being multi-controlled.")
    print("==--==--"*10)

    angle_list = angle_generator.angles
    print(f"Angles (radians): {angle_list}")

    print("==--==--"*10)
    circuit = GroverRudolphCircuit(cardinality=c, num_qubits=4)
    grover_rudolph_circuit = circuit.generate_circuit()
    print(grover_rudolph_circuit)

if __name__ == "__main__":
    main()
import cirq
import math
import numpy as np

from dataclasses import dataclass, field

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
    
#     def generate_circuit(self, verbose: bool = False) -> cirq.Circuit:
#         """
#         Generate a circuit for the Grover-Rudolph algorithm with a given number of qubits and cardinality.
#         The state prepared is a uniform superposition of all subsets of size `card`.
#         Args:
#             num_qbs (int): The number of qubits to use in the circuit.
#             verbose (bool): If True, print additional information about the circuit generation.
#         Returns:
#             cirq.Circuit: The generated circuit.
#         Raises:
#             ValueError: If `card` is less than 2 or if `num_qbs` is less than the number of qubits required to represent `card`.
#         """
   
#         n, c, l = self.num_qubits, self.cardinality, math.ceil(np.log2(self.cardinality)) - 1
#         s = (c - 1) - 2**l
#         angle_lst = GroverRudolphAngles(c).get_angles()
#         tags = self.control_tag_list()
#         # To get the ctrl_sig for i-th element of tags
#         # call:
#         # >>> tags[i][1][-1]
#         ctrl_sig = lambda i: tags[i][1][-1]
#         group = lambda i: tags[i][1][0]

#         qubits = [cirq.NamedQubit(f'x{i}') for i in range(n)]
#         qubits = qubits[::-1] # reverse the qubits for consistency with our convention.
#         # cirq uses little-endian ordering, so we reverse the qubits to match our convention.
#         circuit = cirq.Circuit()

#         if self.cardinality == 2:
#             print(f"The angle is: {float(angle_lst[0])}") if verbose else None
#             circuit.append(cirq.Ry(rads=angle_lst[0]).on(qubits[0]))
#         else:
#             circuit.append(cirq.Ry(rads=angle_lst[0]).on(qubits[0]))
#             print(f"{0+1}th angle: {angle_lst[0]} added. Controlled by non\n") if verbose else None
#             for step in range(3, c + 1):
#                 print(f"Step: {step}") if verbose else None
#                 # recall that we must shift the step by 3
#                 shift_step = step - 3

#                 print(f"Shifted step: {shift_step}") if verbose else None
#                 print(f"Ctrl sig: {ctrl_sig(shift_step)}") if verbose else None
#                 print(f"Group: {group(shift_step)}") if verbose else None
#                 print(f"Target qb: {qubits[group(shift_step)]}") if verbose else None

#                 ctrl_qb_group = qubits[:group(shift_step)] # identify the ctrl qbs
#                 target_qb = qubits[group(shift_step)] # identify the target qb
#                 angle = angle_lst[step - 2] # define the angle
#                 # initialise the ctrl ry gate
#                 ctrl_ry_gate = cirq.Ry(rads=angle).controlled(
#                     num_controls=group(shift_step),
#                     control_values=ctrl_sig(shift_step)
#                 )
#                 circuit.append(ctrl_ry_gate.on(*ctrl_qb_group, target_qb))
#                 print(f"{shift_step + 1}th angle: {angle} added. Controlled by {ctrl_sig(shift_step)}\n") if verbose else None

#         return circuit
    
# class gr_gate(cirq.Gate):
#     def __init__(self, num_qubits: int, card: int):
#         """
#         Initialise the Grover-Rudolph gate with the number of qubits and cardinality.
#         Args:
#             num_qubits (int): The number of qubits in the circuit.
#             card (int): The cardinality of the subset.
#         Raises:
#             ValueError: If `card` is less than 2 or if `num_qubits` is less than the number of qubits required to represent `card`.
#         """
#         if card <= 2:
#             raise ValueError("Cardinality must be greater than 2 for generating gate.")
#         if num_qubits <= 0 or num_qubits < math.ceil(np.log2(card)):
#             raise ValueError("Too few qubits!")
#         self.num_qubits = num_qubits
#         self.card = card
    
#     def _num_qubits_(self) -> int:
#         """
#         Return the number of qubits required for the Grover-Rudolph gate.
#         This is equal to the number of qubits plus one ancilla qubit.
#         """
#         return self.num_qubits
    
#     def _decompose_(self, qubits: list[cirq.Qid]) -> cirq.OP_TREE:
#         if len(qubits) != self.num_qubits:
#             raise ValueError(f"Expected {self.num_qubits} qubits, but got {len(qubits)}.")
        
#         # Generate the circuit as operations
#         gr_circuit = GroverRudolphCircuit(card=self.card)
#         yield from gr_circuit.generate_circuit(num_qbs=self.num_qubits, verbose=True).all_operations()
    

if __name__ == "__main__":
    for c in range(3,15):
        tag = ControlTag(c)
        print(f"Cardinality: {c}")
        print(f"tag.group_number: {tag.group_number}")
        print(f"tag.position_in_group: {tag.position_in_group}")
        print(f"tag.binary_signature: {tag.binary_signature}")
        print(f"tag.control_signature: {tag.control_signature}")
        print("-----")
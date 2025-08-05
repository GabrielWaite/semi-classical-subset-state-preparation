# grover_rudolph_circuit.py
# Gabriel Waite
# 04-10-2024

import cirq
import math
import numpy as np
from grover_rudolph_angles import *

class GroverRudolphCircuit:
    """
    A class to generate a Grover-Rudolph circuit for a given cardinality.
    The circuit prepares a uniform superposition of all subsets of size `card`.
    """
    
    def __init__(self, card: int):
        """
        Initialise the GroverRudolphCircuit with the cardinality.
        Args:
            card (int): The cardinality of the subset.
        Raises:
            ValueError: If the cardinality is less than or equal to 2.
        """
        if card <= 2:
            raise ValueError("Cardinality must be greater than 2 for generating circuit.")
        self.card = card

    def control_tag(self, c: int) -> tuple:
        """
        Generate a tuple of control tag information for the Grover-Rudolph circuit.
        Args:
            c (int): The cardinality of the subset
        Returns:
            tuple: A tuple containing:
                - l: the control number group
                - R: the position in the group
                - bin_sig: binary signature, padded by group number
                - ctrl_sig: control signature
        Note:
            For a given cardinality `card`, we only need a certain number of multi-controlled rotations.
            The number of multi-controls needed is determined by the largest power of 2 that is less than or equal to `card`.
            The group number `l` is determined by the largest power of 2 that is less than or equal to `card - 1`.
            The position `R` is the difference between `card - 1` and this power of 2.
            The binary signature `bin_sig` is the binary representation of `R` padded to the length of `l`.
            The control signature `ctrl_sig` is a list of tuples, where each tuple contains a single integer representing the control value for that bit in `bin_sig`.
        """
        steps = c - 1

        # find the maximum number of individual mutli-controls needed
        l = math.ceil(np.log2(c)) - 1
        # This places us in a specific group that has 2**l possible combinations.
        # We need to find how far into this group we lie.
        # We index the group from 0.
        R = steps - 2**l
        bin_sig = f"{R:0{l}b}"
        ctrl_sig = [(int(i),) for i in bin_sig]
        return l, R, bin_sig, ctrl_sig

    def control_tag_list(self) -> list:
        """
        Generate a list of control tags for the Grover-Rudolph circuit.
        Args:
            card (int): The cardinality of the subset
        Returns:
            list: A list of tuples, each containing:
                - c: the control number group
                - ControlTag: a tuple containing control tag information for that group
        Note:
            The list contains control tags for all groups from 3 to `card`.
            Each tag is a tuple containing the control number group and the corresponding ControlTag.
        """
        if self.card < 3:
            raise ValueError("Cardinality must be at least 3 to generate control tags.")
        # Generate control tags for groups from 3 to card
        # We start from 3 because the angles for 1 and 2 are trivial.
        tags = [(c, self.control_tag(c)) for c in range(3, self.card + 1)]
        return tags
    
    def generate_circuit(self, num_qbs: int, verbose: bool = False) -> cirq.Circuit:
        """
        Generate a circuit for the Grover-Rudolph algorithm with a given number of qubits and cardinality.
        The state prepared is a uniform superposition of all subsets of size `card`.
        Args:
            num_qbs (int): The number of qubits to use in the circuit.
            verbose (bool): If True, print additional information about the circuit generation.
        Returns:
            cirq.Circuit: The generated circuit.
        Raises:
            ValueError: If `card` is less than 2 or if `num_qbs` is less than the number of qubits required to represent `card`.
        """
        if self.card <= 2:
            raise ValueError("Card must be greater than 2")
        if num_qbs <= 0 or num_qbs < math.ceil(np.log2(self.card)):
            raise ValueError("Too few qubits!")

        n, c, l = num_qbs, self.card, math.ceil(np.log2(self.card)) - 1
        s = (c - 1) - 2**l
        angle_lst = GroverRudolphAngles(c).get_angles()
        tags = self.control_tag_list()
        # To get the ctrl_sig for i-th element of tags
        # call:
        # >>> tags[i][1][-1]
        ctrl_sig = lambda i: tags[i][1][-1]
        group = lambda i: tags[i][1][0]

        qubits = [cirq.NamedQubit(f'x{i}') for i in range(n)]
        qubits = qubits[::-1] # reverse the qubits for consistency with our convention.
        # cirq uses little-endian ordering, so we reverse the qubits to match our convention.
        circuit = cirq.Circuit()

        if self.card == 2:
            print(f"The angle is: {float(angle_lst[0])}") if verbose else None
            circuit.append(cirq.Ry(rads=angle_lst[0]).on(qubits[0]))
        else:
            circuit.append(cirq.Ry(rads=angle_lst[0]).on(qubits[0]))
            print(f"{0+1}th angle: {angle_lst[0]} added. Controlled by non\n") if verbose else None
            for step in range(3, c + 1):
                print(f"Step: {step}") if verbose else None
                # recall that we must shift the step by 3
                shift_step = step - 3

                print(f"Shifted step: {shift_step}") if verbose else None
                print(f"Ctrl sig: {ctrl_sig(shift_step)}") if verbose else None
                print(f"Group: {group(shift_step)}") if verbose else None
                print(f"Target qb: {qubits[group(shift_step)]}") if verbose else None

                ctrl_qb_group = qubits[:group(shift_step)] # identify the ctrl qbs
                target_qb = qubits[group(shift_step)] # identify the target qb
                angle = angle_lst[step - 2] # define the angle
                # initialise the ctrl ry gate
                ctrl_ry_gate = cirq.Ry(rads=angle).controlled(
                    num_controls=group(shift_step),
                    control_values=ctrl_sig(shift_step)
                )
                circuit.append(ctrl_ry_gate.on(*ctrl_qb_group, target_qb))
                print(f"{shift_step + 1}th angle: {angle} added. Controlled by {ctrl_sig(shift_step)}\n") if verbose else None

        return circuit
    
class gr_gate(cirq.Gate):
    def __init__(self, num_qubits: int, card: int):
        """
        Initialise the Grover-Rudolph gate with the number of qubits and cardinality.
        Args:
            num_qubits (int): The number of qubits in the circuit.
            card (int): The cardinality of the subset.
        Raises:
            ValueError: If `card` is less than 2 or if `num_qubits` is less than the number of qubits required to represent `card`.
        """
        if card <= 2:
            raise ValueError("Cardinality must be greater than 2 for generating gate.")
        if num_qubits <= 0 or num_qubits < math.ceil(np.log2(card)):
            raise ValueError("Too few qubits!")
        self.num_qubits = num_qubits
        self.card = card
    
    def _num_qubits_(self) -> int:
        """
        Return the number of qubits required for the Grover-Rudolph gate.
        This is equal to the number of qubits plus one ancilla qubit.
        """
        return self.num_qubits
    
    def _decompose_(self, qubits: list[cirq.Qid]) -> cirq.OP_TREE:
        if len(qubits) != self.num_qubits:
            raise ValueError(f"Expected {self.num_qubits} qubits, but got {len(qubits)}.")
        
        # Generate the circuit as operations
        gr_circuit = GroverRudolphCircuit(card=self.card)
        yield from gr_circuit.generate_circuit(num_qbs=self.num_qubits, verbose=True).all_operations()
    

if __name__ == "__main__":
    c: int = 5  # Cardinality
    n: int = 3 # Number of qubits
    gr_circuit = GroverRudolphCircuit(card=c)
    circuit = gr_circuit.generate_circuit(num_qbs=n, verbose=True)
    print(circuit)
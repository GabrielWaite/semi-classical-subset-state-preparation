# main.py
# Gabriel Waite
# 05-10-2024

import cirq
from utility.grover_rudolph_angles  import *
from utility.grover_rudolph_circuit import *
from utility.subset_generator       import *
from utility.subset_permutation     import *
from utility.permutation_circuits   import *


def main(num_qubits: int, cardinality: int, target_subset: list[int], verbose: bool = False) -> cirq.Circuit:
    """
    Main function to generate the full state preparation circuit.
    Args:
        num_qubits (int): Number of qubits in the circuit.
        cardinality (int): Cardinality of the subset.
        target_subset (list[int]): Target subset to prepare.
    """
# --- -- -- - - - Error Checking ---
    if len(target_subset) != cardinality:
        raise ValueError(f"The length of the target subset {target_subset} and the cardinality {cardinality}, do not match!.")
    if max(target_subset) > 2**num_qubits:
        raise ValueError(f"The value {max(target_subset)} exceeds {2**num_qubits - 1}")
    if not all(isinstance(i, int) for i in target_subset):
        raise ValueError(f"Target subset must contain only integers in [{0},{2**num_qubits - 1}]")
# --- -- -- - - - Subset Generation and Permutation ---
    print(f"Generating subset for Grover-Rudolph circuit with cardinality {cardinality}") if verbose else None
    # Generate the Grover-Rudolph subset
    gr_subset = [_ for _ in range(cardinality)]
    print(f"\tGrover-Rudolph subset: {gr_subset}\n") if verbose else None

    print("Generating permutation mapping and cycles from GR subset to target subset") if verbose else None
    # Prepare the subset permutation
    subset_permutation_generator = SubsetPermutation(gr_subset=gr_subset, target_subset=target_subset)
    mapping = subset_permutation_generator.subset_element_matching()[1]
    print(f"\tMapping from GR state {gr_subset} to target subset {target_subset}:\n\t {mapping}\n") if verbose else None

    cycles = subset_permutation_generator.permutation_cycles()
    print(f"\tPermutation cycles for target subset {target_subset}:\n\t {cycles}\n") if verbose else None

# --- -- - - - Grover-Rudolph Circuit Generation ---
    print(f"Generating Grover-Rudolph circuit with cardinality {cardinality} and qubits {num_qubits} -> [x{0},...,x{num_qubits-1}]") if verbose else None
    # Generate the Grover-Rudolph angles
    gr_angle_generator = GroverRudolphAngles(card= cardinality)
    angles = gr_angle_generator.get_angles()
    print(f"\tAngles for cardinality {cardinality}:\n\t {angles}\n") if verbose else None

    # Initialise the circuit and its qubits
    circuit = cirq.Circuit()
    ws_qubits = [cirq.NamedQubit(f'x{i}') for i in range(num_qubits)]
    # ws_qubits = ws_qubits[::-1]  # Reverse the qubits for consistency
    ancilla = cirq.NamedQubit('ancilla')
    qubits = ws_qubits + [ancilla]

    circuit.append(cirq.I.on_each(qubits))
    print("----- ---- --- -- -- -- - - - Initialised Circuit - - - -- -- -- --- --- ---- -----") if verbose else None
    print(circuit) if verbose else None
    print("----- ---- --- -- -- -- - - - Initialised Circuit - - - -- -- -- --- --- ---- -----\n") if verbose else None

    # Create the Grover-Rudolph circuit
    gr_unitary_gate = gr_gate(num_qubits=num_qubits, card=cardinality)
    circuit.append(gr_unitary_gate.on(*ws_qubits))
    print("\tGrover-Rudolph circuit generated.") if verbose else None
    circuit = cirq.Circuit(cirq.decompose_once_with_qubits(gr_unitary_gate, qubits))
    print("----- ---- --- -- -- -- - - - GR Circuit - - - -- -- -- --- --- ---- -----") if verbose else None
    circuit.append(cirq.I.on_each(qubits))
    print(circuit) if verbose else None
    print("----- ---- --- -- -- -- - - - GR Circuit - - - -- -- -- --- --- ---- -----\n") if verbose else None

# --- -- - - - Permutation Circuit Generation ---
    print("Generating permutation circuit based on cycles") if verbose else None
    print(cycles) if verbose else None
    for cycle in cycles:
        unitary_gate = permutation_cycle_gate(num_qubits, cycle)
        circuit.append(unitary_gate.on(*qubits))
        print("----- ---- --- -- -- -- - - - GR Circuit + Cycle - - - -- -- -- --- --- ---- -----") if verbose else None
        print(circuit) if verbose else None
        print("----- ---- --- -- -- -- - - - GR Circuit + Cycle - - - -- -- -- --- --- ---- -----\n") if verbose else None

    return circuit

if __name__ == "__main__":
    # Example usage
    num_qubits = 5
    cardinality = 6
    target_subset = SubsetGenerator(n= num_qubits, card= cardinality).generate_subset()
    print(f"Target subset: {target_subset}\n")

    circuit = main(num_qubits, cardinality, target_subset)
    # The circuit doesn't look too nice so we won't print it here.
    sv = circuit.final_state_vector()
    print(f"Final state vector: \n\t{cirq.dirac_notation(sv)}\n")
    print(f"Target subset in (padded) binary form: \n\t{[bin(i)[2:].zfill(num_qubits+1) for i in target_subset]}")
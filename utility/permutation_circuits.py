# permutation_circuits.py
# Gabriel Waite
# 04-10-2024

import cirq

def gray_code_rotation_circuit(num_qubits: int, gray_code_vector: list[int]) -> cirq.Circuit:

    if num_qubits < 0:
        raise ValueError("Number of qubits must be non-negative.")
    if not all(isinstance(bit, int) for bit in gray_code_vector):
        raise ValueError("Gray code vector must contain only integers (0 or 1).")   
    if len(gray_code_vector) != num_qubits:
        raise ValueError("Gray code vector length must match the number of qubits.")
    
    # Create a circuit for the Gray code rotation
    qubits = [cirq.NamedQubit(f'x_{i}') for i in range(0, num_qubits)]
    # NOTE: we might have to reverse this!!
    circuit = cirq.Circuit()

    for i, bit in enumerate(gray_code_vector):
        if bit == 1:
            circuit.append(cirq.X(qubits[i]))
    
    return circuit

class gray_code_gate(cirq.Gate):
    """
    A custom gate for the Gray code rotation between two binary strings.
    This gate applies a Pauli X to qubit 'i' if the i-th bits of the
    two binary strings are different.
    """

    def __init__(self, num_qubits: int, binary_str_1: str, binary_str_2: str):
        if num_qubits < 0:
            raise ValueError("Number of qubits must be non-negative.")
        if len(binary_str_1) != num_qubits or len(binary_str_2) != num_qubits:
             raise ValueError("Length of binary strings must match the number of qubits.")

        super().__init__() # It's good practice to call the parent's initializer
        self._num_qubits = num_qubits
        self.binary_str_1 = binary_str_1
        self.binary_str_2 = binary_str_2

    def _num_qubits_(self):
        """This method is required by the cirq.Gate interface."""
        return self._num_qubits

    def _decompose_(self, qubits):
        """Applies X gates to the qubits based on the Gray code vector."""
        # Calculate the bitwise XOR between the two strings
        gray_code_vector = [int(b1) ^ int(b2) for b1, b2 in zip(self.binary_str_1, self.binary_str_2)]

        # Yield an X operation for each '1' in the resulting vector
        for i, bit in enumerate(gray_code_vector):
            if bit == 1:
                yield cirq.X(qubits[i])

    def _circuit_diagram_info_(self, args: cirq.CircuitDiagramInfoArgs):
        # Create a more descriptive label for the gate
        label = f"V({self.binary_str_1},{self.binary_str_2})"
        return cirq.CircuitDiagramInfo(
            wire_symbols=(label,) + (None,) * (self._num_qubits - 1),
            connected=True,
        )

    def __repr__(self):
        return f"gray_code_gate(num_qubits={self._num_qubits}, binary_str_1='{self.binary_str_1}', binary_str_2='{self.binary_str_2}')"


def bin_ctrl_tag(binary_string: str) -> list[int]:
    """
    Convert a binary string to a control tag (list of integers).
    Args:
        binary_string (str): A binary string (e.g., '101').
    Returns:
        list[int]: A list of integers representing the control tag.
    """
    return [(int(bit),) for bit in binary_string]

"""
A cycle unitary U_c = (\prod_{i=0}^{l-1} g_i) B_0


c_i = (x_{i_0}, x_{i_1}, ..., x_{i_{l-1}}) is a cycle of length l

Take a k in {0,1,...,l-1} and consider, the k-th element of the cycle c_i is x_{i_k}.
The gate g_k is defined as:
g_k = C_{x_{i_k}}X . CV_{i_k} 

The gate C_{x_{i_k}}X is a multi-controlled X gate with n control qubits  and target is an ancilla qubit.
    Specifically, C_{x_{i_k}} is a multi-control over n qubits governed by the actual binary value x_{i_k}.
    To get the control values, we can use the bin_ctrl_tag function.
    bin_multi_ctrl = cirq.X.controlled(
                    num_controls=n,
                    control_values=bin_ctrl_tag(x_{i_k})
                )
    circuit.append(bin_multi_ctrl.on(*qubits, ancilla_qubit))

The gate CV_{i_k} is a controlled V (gray code) gate with control qubit ancilla qubit and target qubits x_{i_0}, ..., x_{i_{k-1}}.
    ctrl_gray_code_gate = gray_code_gate(
                    num_qubits=n,
                    binary_str_1=x_{i_k},
                    binary_str_2=x_{i_{k+1}}
                ).controlled(
                    num_controls=1,
                    control_values=(1,)
                    )
    circuit.append(ctrl_gray_code_gate.on(ancilla_qubit, *qubits)
"""

class g_gate(cirq.Gate):
    def __init__(self, num_qubits: int, cycle: list[int]):
        if num_qubits < 0:
            raise ValueError("Number of qubits must be non-negative.")
        self._num_qubits = num_qubits
        self.cycle = cycle

    def _num_qubits_(self):
        """This method is required by the cirq.Gate interface."""
        return self._num_qubits + 1  # +1 for the ancilla qubit
    
    def _decompose_(self, qubits):
        """Applies the g_k gate to the qubits based on the cycle and element index."""
        if self.element_index < 0 or self.element_index >= len(self.cycle):
            raise ValueError("Element index is out of bounds for the cycle.")

        workspace_qubits = qubits[:-1]  # All but the last qubit are workspace qubits
        ancilla_qubit = qubits[-1]  # The last qubit is the ancilla qubit
        l = len(self.cycle)

        for k in range(l):
            x_k, x_kp1 = self.cycle[k], self.cycle[(k + 1) % l]  # Wrap around to the start of the cycle
            bin_k, bin_kp1 = bin(x_k)[2:].zfill(self._num_qubits), bin(x_kp1)[2:].zfill(self._num_qubits)

            # Get control tag
            control_tag = bin_ctrl_tag(bin(x_k)[2:].zfill(self._num_qubits))

            # --- Step 1: Mark state x_k using multi-controlled X on ancilla
            mcx_gate = cirq.X.controlled(
                num_controls=self._num_qubits,
                control_values=control_tag
            )
            yield mcx_gate.on(*workspace_qubits, ancilla_qubit)

            # --- Step 2: Apply controlled Gray code gate from x_k to x_{k+1}
            gc_gate = gray_code_gate(num_qubits=self._num_qubits, binary_str_1=bin_k, binary_str_2=bin_kp1)
            controlled_gc = gc_gate.controlled(num_controls=1, control_values=[1])
            yield controlled_gc.on(ancilla_qubit, *workspace_qubits)

        # --- Step 3: apply C_{x_0}X again to uncompute ancilla
        x_0 = self.cycle[0]
        bin_0 = bin(x_0)[2:].zfill(self._num_qubits)
        ctrl_vals_0 = bin_ctrl_tag(bin_0)
        mcx_final = cirq.X.controlled(num_controls=self._num_qubits, control_values=ctrl_vals_0)
        yield mcx_final.on(*workspace_qubits, ancilla_qubit)

        def _circuit_diagram_info_(self, args: cirq.CircuitDiagramInfoArgs):
            return [f"U_c"] * (self._num_qubits + 1)

class permutation_cycle_gate(cirq.Gate):
    def __init__(self, num_qubits: int, cycle: list[int]):
        self.n = num_qubits
        self.cycle = cycle
        if not all(0 <= x < 2**num_qubits for x in cycle):
            raise ValueError("Cycle contains integers outside range for n-bit strings.")
    
    def _num_qubits_(self):
        return self.n + 1  # n data + 1 ancilla

    def _decompose_(self, qubits):
        data_qubits = qubits[:self.n]
        ancilla = qubits[self.n]
        l = len(self.cycle)

        for k in range(l):
            x_k, x_kp1 = self.cycle[k], self.cycle[(k + 1) % l]
            bin_k = bin(x_k)[2:].zfill(self.n)
            bin_kp1 = bin(x_kp1)[2:].zfill(self.n)

            # Step 1: Mark state x_k using MCX
            ctrl_vals = tuple(int(b) for b in bin_k)
            mcx_gate = cirq.X.controlled(num_controls=self.n, control_values=ctrl_vals)
            yield mcx_gate.on(*data_qubits, ancilla)

            # Step 2: Gray code gate controlled by ancilla
            gc_gate = gray_code_gate(self.n, bin_k, bin_kp1)
            controlled_gc = gc_gate.controlled(num_controls=1, control_values=[1])
            yield controlled_gc.on(ancilla, *data_qubits)

        # Step 3: Uncompute ancilla
        x_0 = self.cycle[0]
        bin_0 = bin(x_0)[2:].zfill(self.n)
        ctrl_vals_0 = tuple(int(b) for b in bin_0)
        mcx_final = cirq.X.controlled(num_controls=self.n, control_values=ctrl_vals_0)
        yield mcx_final.on(*data_qubits, ancilla)

def permutation_circuit(num_qubits: int, cycles: list[list[int]]) -> cirq.Circuit:
    """
    Generate a circuit for the permutation defined by the cycles.
    Args:
        num_qubits (int): The number of qubits in the circuit.
        cycles (list[list[int]]): A list of cycles, where each cycle is a list of indices.
    Returns:
        cirq.Circuit: The circuit representing the permutation.
    """
    if num_qubits < 0:
        raise ValueError("Number of qubits must be non-negative.")
    
    workspace_qubits = [cirq.NamedQubit(f'x_{i}') for i in range(n)]  # Create data qubits
    ancilla_qubit = cirq.NamedQubit('ancilla')  # Create an ancilla qubit
    qubits = workspace_qubits + [ancilla_qubit]  # Combine data and
    circuit = cirq.Circuit()
    for cycle in cycles:
        gate = permutation_cycle_gate(num_qubits, cycle)
        circuit.append(gate.on(*qubits))
    
    return circuit

if __name__ == "__main__":
    # Define cycle and number of data qubits
    cycle = [0, 1, 3, 9]
    n = 4

    # Create qubits
    data_qubits = cirq.LineQubit.range(n)
    ancilla = cirq.LineQubit(n)

    # Instantiate custom gate and add to circuit
    gate = permutation_cycle_gate(n, cycle)
    circuit = cirq.Circuit(gate.on(*data_qubits, ancilla))
    circuit = cirq.Circuit(
        cirq.decompose_once_with_qubits(gate, data_qubits + [ancilla])
    )
    print(circuit)
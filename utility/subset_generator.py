# subset_generator.py
# Gabriel Waite
# 04-10-2024


class SubsetGenerator:
    def __init__(self, n: int, card: int):
        """
        Initialize the SubsetGenerator with the number of qubits and cardinality.
        Args:
            n (int): The number of qubits in the system.
            card (int): The cardinality of the resulting subset.
        """
        self.n = n
        self.card = card

    def __repr__(self):
        return f"SubsetGenerator(n: {self.n}, card: {self.card})"
    
    def generate_subset(self) -> list:
        """
        Generate a subset of elements for the SCSS |C>.
        This is a fixed set of elements based on the number of qubits.
        The sequence is defined as powers of 2, that is, [1, 2, 4, ..., 2^(n-1)].
        Args:
            n (int): The number of qubits in the system.
        Returns:
            list: A list of elements generated based on the input parameter.
        Raises:
            ValueError: If n is negative.
        """
        if self.n < 0:
            raise ValueError("n must be non-negative")
        if self.n == 0:
            return [0]

        # Generate a list of O(n) elements
        return [1 << i for i in range(self.n)]
    
    def generate_custom_subset(self, subset: list, subset_type: str = "D"):
        """
        Input a custom subset of elements for the SCSS |C> to verify its form.
        Given subsets must contain elements that are either encoded in decimal or binary format.
        The range of the elements must be within 0 to 2^n - 1, where n is the number of qubits.
        The cardinality of the subset not be exponentially large.
        Args:
            subset (list): The custom subset of elements.
            subset_type (str): Type of subset, default is "D" for DECIMAL.
                               Other options can be "B" for BINARY.
        Returns:
            none: If the subset is valid, it returns None.
        Raises:
            ValueError: If the subset is not valid.
        Note:
            ** We do not check if the subset is polynomially bounded **
            ** This is assumed to be checked by the caller. **
        """
        # Check subset existence
        if not subset:
            raise ValueError("Subset cannot be empty")
        
        # Check cardinality
        if len(subset) != self.card:
            raise ValueError(f"Cardinality mismatch: expected {self.card}, got {len(subset)}")
        
        # Check elements in the subset
        if subset_type == "D":  
            # Check if the subset is a valid decimal representation
            for i in range(self.card):
                if subset[i] < 0 or subset[i] >= (1 << self.n):
                    raise ValueError(f"Element {subset[i]} at index {i} is out of bounds for n={self.n}")
        elif subset_type == "B":
            # Check if the subset is a valid binary representation
            for i in range(self.card):
                if not isinstance(subset[i], int) or subset[i] < 0 or subset[i] >= (1 << self.n):
                    raise ValueError(f"Element {subset[i]} at index {i} is not a valid binary representation for n={self.n}")
        else:
            raise ValueError("Invalid subset type. Use 'D' for decimal or 'B' for binary.")
        
        # If all checks pass, return None
        return None
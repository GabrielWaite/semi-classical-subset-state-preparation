# subset_permutation.py
# Gabriel Waite
# 04-10-2024

"""
For a given cardinality `c', we must map each value j in {0,1,...,c-1} to a specific value x in the chosen subset.

From the GR state, we know we have n_gr = math.ceil(math.log2(c)) qubits.
For the subset state we want, we have a fixed number of qubits, n_sub.

Essentially, we want to permute the elements of the GR state to match the subset state.
let the GR set be denoted G and the target SCSS subset be denoted S.

For simplicity, G[i]-> S[i] for i in range(len(S)).
"""

class SubsetPermutation:
    def __init__(self, gr_subset: list[int], target_subset: list[int]):
        """
        Initialize the SubsetPermutation with the GR subset and target subset.
        Args:
            gr_subset (list[int]): The Grover-Rudolph subset.
            target_subset (list[int]): The target subset to match.
        """
        self.gr_subset = gr_subset
        self.target_subset = target_subset

    def __repr__(self):
        return f"SubsetPermutation(GR: {self.gr_subset}, Target: {self.target_subset})"
    
    def subset_element_matching(self) -> dict[int, int]:
        """
        Maps elements from the GR subset to the target subset based on their indices.
        Returns:
            dict[int, int]: A dictionary mapping each element in the GR subset to its corresponding element in the target subset.
        Raises:
            ValueError: If the lengths of the two subsets do not match.
        Note:
            When calling this, pass the GR subset first and the target subset second.
        """
        if len(self.gr_subset) != len(self.target_subset):
            raise ValueError("Subsets must be of the same length to create a mapping.")
        
        mapping = {}
        for i in range(len(self.gr_subset)):
            mapping[self.gr_subset[i]] = self.target_subset[i]

        def dict_to_str(d: dict[int, int]) -> str:
            return ', '.join(f"{k} -> {v}" for k, v in d.items())
        
        return mapping, dict_to_str(mapping)
    
    def permutation_cycles(self) -> list[list[int]]:
        """
        Find the cycles in a sparse permutation defined by the target subset.
        Returns:
            list[list[int]]: A list of cycles, where each cycle is represented as a list of indices.
        Note:
            This function identifies cycles in the permutation defined by the target subset.
            Each cycle is a sequence of indices where each index points to the next index in the cycle.
            Fixed points (where an index points to itself) are not included in the cycles.
        """
        d = len(self.target_subset)
        used = [False] * d # Track used indices
        cycles = []  # List to store cycles

        for i in range(d):
            if used[i] or self.target_subset[i] == i:
                continue

            cycle = [i, self.target_subset[i]] # Start a new cycle with the current index and its target
            j = self.target_subset[i]

            while j < d:
                used[j] = True
                j = self.target_subset[j]
                cycle.append(j)

            cycles.append(cycle)

        return cycles

if __name__ == "__main__":
    # Example usage of the SubsetPermutation class
    gr_subset = [0, 1, 2, 3]
    target_subset = [2, 4, 6, 8]

    sp = SubsetPermutation(gr_subset, target_subset)

    print("--- -- -- - - -")
    print(sp)
    print("--- -- -- - - -")

    mapping = sp.subset_element_matching()[1]
    print(f"Mapping from GR state {gr_subset} to target subset {target_subset}: {mapping}\n")

    cycles = sp.permutation_cycles()
    print(f"Permutation cycles for target subset {target_subset}: {cycles}\n")
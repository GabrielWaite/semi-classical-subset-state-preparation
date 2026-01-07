from dataclasses import dataclass, field
from functools import cached_property

def dictionary_to_string(d: dict[int, int]) -> str:
    """
    Convert a dictionary to a string representation.

    Args:
        d (dict[int, int]): The dictionary to convert.

    Returns:
        str: The string representation of the dictionary.
    """
    return ", ".join(f"{k}: {v}" for k, v in d.items())

@dataclass
class SubsetPermutation:
    gr_subset: list[int]
    target_subset: list[int]
    _subset_length: int = field(init=False)

    def __post_init__(self):
        if not self.gr_subset or not self.target_subset:
            raise ValueError("Both GR and Target subsets must be provided.")
        if len(self.gr_subset) != len(self.target_subset):
            raise ValueError("GR and Target subsets must have the same length.")
        
        self._subset_length = len(self.gr_subset)

    def __str__(self):
        return f"GR Subset: {self.gr_subset}, Target Subset: {self.target_subset}"

    @cached_property
    def get_subset_element_map(self) -> dict[int, int]:
        """
        Get the mapping of elements from the GR subset to the target subset.

        Returns:
            dict[int, int]: A dictionary mapping elements from the GR subset to the target subset.
        """
        mapping_dict: dict[int, int] = {gr: target for gr, target in zip(self.gr_subset, self.target_subset)}
        dictionary_str: str = dictionary_to_string(mapping_dict)
        return mapping_dict, dictionary_str

    def get_permutation_cycles(self) -> list[list[int]]:
        """
        Get the permutation cycles from the GR subset to the target subset.

        Returns:
            list[list[int]]: A list of permutation cycles.
        """
        used_indices: list[bool] = [False] * self._subset_length
        cycles: list[list[int]] = []

        for i in range(self._subset_length):
            if used_indices[i] or self.target_subset[i] == i:
                continue

            j = self.target_subset[i]
            cycle: list[int] = [i, j] # Start a new cycle with the current index and its target.

            while j < self._subset_length and not used_indices[j]:
                used_indices[j] = True
                j = self.target_subset[j]
                cycle.append(j)

            cycles.append(cycle)

        return cycles
    
def main():
    gr_subset = [0,1,2,3]
    targ_subset = [2,4,6,8]

    sp = SubsetPermutation(gr_subset, targ_subset)
    print("--- -- -- - - -")
    print(sp)
    print("--- -- -- - - -")

    mapping = sp.get_subset_element_map[1]
    print(f"Mapping from GR state {gr_subset} to target subset {targ_subset}: {mapping}\n")

    cycles = sp.get_permutation_cycles()
    print(f"Permutation cycles for target subset {targ_subset}: {cycles}\n")

if __name__ == "__main__":
    main()


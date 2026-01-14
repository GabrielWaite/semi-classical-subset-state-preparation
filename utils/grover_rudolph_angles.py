from functools import cached_property
import math 
from dataclasses import dataclass

@dataclass
class GroverRudolphAngles:
    """
    A class to generate angles for the Grover-Rudolph algorithm based on the cardinality of the subset.
    """
    cardinality: int

    def __post_init__(self):
        if self.cardinality <= 2:
            raise ValueError("Cardinality must be greater than 2.")

    @cached_property
    def multi_control_prefixes(self) -> list[str]:
        """
        Compute the prefixes for the sequence of multi-controlled gates in the GR circuit.

        Args:
            None

        Returns:
            list[str]: A list of binary strings representing the prefixes.

        Notes:
          !! we DO add the trivial '' control sequence !!           
            The required length of the prefixes changes as the circuit goes into different "layers".
            By design, for cardinalities greater than 2, there is a rotation gate applied at the start that has no control. Thus the expected number of prefixes should be the cardinality minus 2.
        Example:
            For a cardinality of 4, the prefixes would be:
            0, 1
        """
        num: int = self.cardinality - 2
        result: list[str] = []
        length: int = 1

        while len(result) < num:
            for i in range(2**length):
                result.append(bin(i)[2:].zfill(length))
                if len(result) == num: return [''] + result
            length += 1
        return [''] + result
    
    def get_partition_counter_from_prefix(self, prefix: str) -> tuple[int, int]:
        """
        Compute the partition counter from a given prefix.

        Args:
            prefix (str): A binary string representing the prefix.

        Returns:
            tuple[int, int]: A tuple representing the partition counter.
        """
        bit_length: int = math.ceil(math.log2(self.cardinality)) # Number of bits needed
        prefix_length: int = len(prefix)
        binary_values: list[str] = [f"{i:0{bit_length}b}" for i in range(self.cardinality)] # Generate all binary values from 0 to cardinality-1; all of them have the same bit length

        # Reverse the binary values
        reversed_binary_values: list[str] = [bv[::-1] for bv in binary_values]

        # List the og bv and the truncated string
        conditional_binary_values: list[tuple[str, str]] = [(bv, bv[prefix_length:]) for bv in reversed_binary_values if bv[:prefix_length] == prefix]

        # List matchings
        list_N0: list[str] = [bv for bv in conditional_binary_values if bv[1][0] == '0']
        list_N1: list[str] = [bv for bv in conditional_binary_values if bv[1][0] == '1']
        N0: int = len(list_N0)
        N1: int = len(list_N1)

        return N0, N1
    
    @staticmethod
    def compute_partition_angle(N0: int, N1: int) -> float:
        """
        Compute the partition angle for the Grover-Rudolph algorithm.

        Args:
            N0 (int): The number of elements in the |0> partition.
            N1 (int): The number of elements in the |1> partition.

        Returns:
            float: The partition angle in radians.
        """
        if N0 + N1 == 0:
            raise ValueError("The sum of N0 and N1 must be greater than 0.")
        return 2 * math.acos(math.sqrt(N0 / (N0 + N1)))

    @cached_property
    def angles(self) -> list[float]:
        """
        Compute the angles for the Grover-Rudolph algorithm.

        Args:
            None

        Returns:
            list[float]: A list of angles in radians.
        """
        angles: list[float] = []
        prefixes: list[str] = self.multi_control_prefixes

        for prefix in prefixes:
            N0, N1 = self.get_partition_counter_from_prefix(prefix)
            angle = self.compute_partition_angle(N0, N1)
            print(f"Prefix: {prefix}, N0: {N0}, N1: {N1}, Angle: {angle}")
            angles.append(angle)

        return angles

def main():
    """ Example """
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
# grover_rudolph_angles.py
# Gabriel Waite
# 04-10-2024


import math

class GroverRudolphAngles:
    """
    A class to generate angles for the Grover-Rudolph algorithm based on the cardinality of the subset.
    The angles are calculated using the PartitionCounter and PartitionAngle functions.
    """
    
    def __init__(self, card: int):
        """
        Initialise the GroverRudolphAngles with the cardinality.
        Args:
            card (int): The cardinality of the subset.
        Raises:
            ValueError: If the cardinality is less than or equal to 2.
        """
        if card <= 2:
            raise ValueError("Cardinality must be greater than 2 for generating angles.")
        self.card = card
    
    def generate_prefix_binary_sequence(self) -> list[str]:
        """
        For a given cardinality, generate a list of binary strings that represent the prefix binary sequence.
        The prefix binary sequence corresponds to the binary representations of the multi-control gates in quantum circuits.
        """
        if self.card <= 2:
            return []

        num_to_generate = self.card - 2
        result_list = []
        length = 1

        while len(result_list) < num_to_generate:
            num_strings_at_length = 2 ** length

            for i in range(num_strings_at_length):
                binary_string = bin(i)[2:].zfill(length)
                result_list.append(binary_string)

                if len(result_list) == num_to_generate:
                    return result_list

            length += 1

        return result_list
    
    def partition_counter(self, prefix: str) -> tuple:
        """
        Count the number of elements in the partition based on the prefix.
        Args:
            prefix (str): The prefix binary string.
        Returns:
            tuple: A tuple containing counts of N0 and N1.
        Raises:
            ValueError: If the cardinality is less than or equal to 2.
        """
        if self.card <= 2:
            raise ValueError("Cardinality must be greater than 2 for partitioning.")
        
        n = math.ceil(math.log2(self.card))
        l = len(prefix)  # Length of the prefix
        bin_vals = [f"{i:0{n}b}" for i in range(self.card)] # Generate binary values from 0 to card
        # Reverse the binary values
        rev_bin_vals = [i[::-1] for i in bin_vals]
        # Make list of original binary string and truncated string
        cond_bin_vals = [(i, i[l:]) for i in rev_bin_vals if i[:l] == prefix]
        list_N0 = [i for i in cond_bin_vals if i[1][0] == '0']
        list_N1 = [i for i in cond_bin_vals if i[1][0] == '1']
        N0 = len(list_N0)
        N1 = len(list_N1)
        return N0, N1 
    
    def partition_angle(self, N0: int, N1: int) -> float:
        """
        Calculate the angle for the partition based on the counts of N0 and N1.
        Args:
            N0 (int): Count of elements in partition N0.
            N1 (int): Count of elements in partition N1.
        Returns:
            float: The calculated angle in radians.
        Raises:
            ValueError: If both N0 and N1 are zero.
        Note:
            We double the angle here.
        """
        if N0 + N1 == 0:
            raise ValueError("N0 and N1 cannot both be zero.")
        return 2 * math.acos(math.sqrt(N0 / (N0 + N1)))
    
    def get_angles(self) -> list[float]:
        """
        Generate angles for the Grover-Rudolph circuit based on the cardinality.
        The angles are calculated using the PartitionCounter and PartitionAngle functions.
        Returns:
            list: A list of angles in radians.
        """
        binary_sequence = [''] + self.generate_prefix_binary_sequence()
        angle_lst = []
        
        for prefix in binary_sequence:
            N0, N1 = self.partition_counter(prefix)
            angle = self.partition_angle(N0, N1)
            angle_lst.append(angle)
        
        return angle_lst


if __name__ == "__main__":
    # Example usage
    card: int = 5
    angles_generator = GroverRudolphAngles(card)
    binary_sequence: list[str] = [''] + angles_generator.generate_prefix_binary_sequence()
    print(f"\nPrefix binary sequence for cardinality {card}: {binary_sequence}")
    print(f"We will expect {card-1} angles, with {card-2} being controlled.\n")

    print("==--==--"*10)
    angle_lst: list[float] = []
    for prefix in binary_sequence:
        N0, N1 = angles_generator.partition_counter(prefix)
        angle = angles_generator.partition_angle(N0, N1)
        print(f"Prefix: '{prefix}', N0: {N0}, N1: {N1}, Angle: {angle:.10f} radians")
        angle_lst.append(angle)
    print("==--==--"*10)
    print(f"Angles for cardinality {card}: {angle_lst}")
    print("==--==--"*10)
    print(angles_generator.get_angles())


    # print(f"Partition Values for prefix '' at cardinality {card}:")
    # print(PartitionCounter(card, ''))
    # print()
    # print(f"Angle for prefix '' at cardinality {card}: {PartitionAngle(*PartitionCounter(card, ''))}\n")
    # print("==--==--"*10)
    # print(f"Partition Values for prefix '0' at cardinality {card}:")
    # print(PartitionCounter(card, '0'))
    # print()
    # print(f"Angle for prefix '0' at cardinality {card}: {PartitionAngle(*PartitionCounter(card, '0'))}\n")

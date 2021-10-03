# Optimized sequence numbers generator to find 666th partition number
# Exercise following https://www.youtube.com/watch?v=iJ8pnCO0nTY


def generate_n_partition_numbers(n: int):
    """
    A partition number of N is the number of unique sums of positive integers that result in N.
    """
    partition_numbers = [1, 1]
    # Sequence of negative indexes to operate
    # The operation sequence is ++--++--++-- etc
    operand_indexes = [1]
    # Index of the current break_distance in the sequence of break_distances
    break_sequence_index = 0
    # Index at which a new operand needs to be appended to the operand list
    next_op_index = 2
    for i in range(len(partition_numbers), n):
        if i >= next_op_index:
            break_sequence_index += 1
            break_distance = 0
            if break_sequence_index & 0b1 == 0:
                break_distance = int(break_sequence_index / 2) + 1
            else:
                break_distance = break_sequence_index + 2
            operand_indexes.append(next_op_index)
            next_op_index += break_distance

        next_num = 0
        for (idx, op_index) in enumerate(operand_indexes):
            # operand is plus if the idx or idx-1 is divisible by 4
            if idx & 0b10 == 0:
                next_num += partition_numbers[-op_index]
            else:
                next_num -= partition_numbers[-op_index]
        partition_numbers.append(next_num)
    return partition_numbers


partition_numbers = generate_n_partition_numbers(667)
print(partition_numbers[-1])

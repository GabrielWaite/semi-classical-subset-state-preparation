# semi-classical-subset-state-preparation
A repository for Python files containing information pertaining to the preparation of quantum states know as *semi-classical subset states*.

For a subset $C \subset \{0,1\}^n$ such that $|C| = {\rm poly}(n)$, we define a *semi-classical subset state* (SCSS) as:
$$|C\rangle = \frac{1}{\sqrt{|C|}} \sum_{x\in C} |x\rangle.$$

## Grover-Rudolph Preparation
To prepre the state, we first prepare a uniform superposition state over the computational basis states from $|0\rangle$ to $|k-1\rangle$, where $k = |C|$.

## Permutation Circuit
We then define a permutation from the elements $\{0,1,\ldots,k-1\}$ to the elements of the target subset $C$.

## References:
*A simple quantum algorithm to efficiently prepare sparse states* - [arXiv](https://arxiv.org/pdf/2310.19309)

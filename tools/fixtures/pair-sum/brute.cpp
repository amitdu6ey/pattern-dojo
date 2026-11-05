#include <vector>

// Check every pair. Correct, but O(n^2) time.
long long countPairs(std::vector<long long>& a, long long k) {
    long long pairs = 0;
    for (size_t i = 0; i < a.size(); ++i)
        for (size_t j = i + 1; j < a.size(); ++j)
            if (a[i] + a[j] == k) ++pairs;
    return pairs;
}

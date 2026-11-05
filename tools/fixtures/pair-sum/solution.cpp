#include <unordered_map>
#include <vector>

// Count index pairs (i < j) with a[i] + a[j] == k. One pass with a hash map of values seen so far.
long long countPairs(std::vector<long long>& a, long long k) {
    std::unordered_map<long long, long long> seen;
    seen.reserve(a.size() * 2);
    long long pairs = 0;
    for (long long x : a) {
        auto it = seen.find(k - x);
        if (it != seen.end()) pairs += it->second;
        ++seen[x];
    }
    return pairs;
}

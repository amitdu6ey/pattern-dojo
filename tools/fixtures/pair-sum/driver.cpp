#include <cstdio>
#include <vector>
#include "solution.cpp"

int main() {
    int n;
    long long k;
    if (std::scanf("%d %lld", &n, &k) != 2) return 1;
    std::vector<long long> a(n);
    for (int i = 0; i < n; ++i) std::scanf("%lld", &a[i]);
    std::printf("%lld\n", countPairs(a, k));
    return 0;
}

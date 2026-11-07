#include <cstdio>
#include <vector>
#include "solution.cpp"

int main() {
    int r, c;
    if (std::scanf("%d %d", &r, &c) != 2) return 1;
    std::vector<std::vector<int>> grid(r, std::vector<int>(c));
    for (int i = 0; i < r; i++)
        for (int j = 0; j < c; j++) std::scanf("%d", &grid[i][j]);
    std::printf("%d\n", orangesRotting(grid));
    return 0;
}

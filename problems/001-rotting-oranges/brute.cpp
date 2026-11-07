#include <utility>
#include <vector>
using namespace std;

// Simulate each minute by scanning the whole grid. Correct, but O((R*C)^2) on a long winding path.
int orangesRotting(vector<vector<int>>& grid) {
    int n = grid.size(), m = grid[0].size(), minutes = 0;
    int dx[] = {1, -1, 0, 0}, dy[] = {0, 0, 1, -1};
    while (true) {
        vector<pair<int, int>> toRot;
        for (int i = 0; i < n; i++)
            for (int j = 0; j < m; j++) {
                if (grid[i][j] != 1) continue;
                for (int d = 0; d < 4; d++) {
                    int ni = i + dx[d], nj = j + dy[d];
                    if (ni >= 0 && nj >= 0 && ni < n && nj < m && grid[ni][nj] == 2) {
                        toRot.push_back({i, j});
                        break;
                    }
                }
            }
        if (toRot.empty()) break;
        for (auto& c : toRot) grid[c.first][c.second] = 2;
        minutes++;
    }
    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
            if (grid[i][j] == 1) return -1;
    return minutes;
}

#include <queue>
#include <vector>
using namespace std;

// Multi-source BFS: every rotten orange starts in the queue, and each pass over the queue is one minute.
int orangesRotting(vector<vector<int>>& grid) {
    int n = grid.size(), m = grid[0].size(), fresh = 0, minutes = 0;
    queue<pair<int, int>> q;
    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++) {
            if (grid[i][j] == 2) q.push({i, j});
            else if (grid[i][j] == 1) fresh++;
        }
    int dx[] = {1, -1, 0, 0}, dy[] = {0, 0, 1, -1};
    while (!q.empty() && fresh > 0) {
        for (int sz = q.size(); sz > 0; sz--) {  // exactly the oranges that were rotten at the start of this minute
            auto [x, y] = q.front();
            q.pop();
            for (int d = 0; d < 4; d++) {
                int nx = x + dx[d], ny = y + dy[d];
                if (nx < 0 || ny < 0 || nx >= n || ny >= m || grid[nx][ny] != 1) continue;
                grid[nx][ny] = 2;  // mark when queued, so no orange is queued twice
                fresh--;
                q.push({nx, ny});
            }
        }
        minutes++;
    }
    return fresh == 0 ? minutes : -1;
}
